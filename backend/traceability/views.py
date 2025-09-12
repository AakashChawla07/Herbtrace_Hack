from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import HerbSpecies, Collector, Batch, ProcessingEvent, QualityTest, ConsumerVerification
from .serializers import (
    HerbSpeciesSerializer, CollectorSerializer, CollectorCreateSerializer,
    BatchSerializer, BatchCreateSerializer, BatchDetailSerializer, BatchStatsSerializer,
    ProcessingEventSerializer, QualityTestSerializer, ConsumerVerificationSerializer
)

class HerbSpeciesViewSet(viewsets.ModelViewSet):
    queryset = HerbSpecies.objects.all()
    serializer_class = HerbSpeciesSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'scientific_name', 'sanskrit_name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.select_related('user').prefetch_related('specializations')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['certification_level', 'is_verified']
    search_fields = ['collector_id', 'user__first_name', 'user__last_name']
    ordering_fields = ['collector_id', 'created_at', 'experience_years']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CollectorCreateSerializer
        return CollectorSerializer
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find collectors near a given location"""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = float(request.query_params.get('radius', 50))
        
        if not lat or not lng:
            return Response({'error': 'lat and lng parameters required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        point = Point(float(lng), float(lat), srid=4326)
        collectors = self.queryset.filter(
            location__distance_lte=(point, Distance(km=radius_km))
        ).annotate(
            distance=Distance('location', point)
        ).order_by('distance')
        
        serializer = self.get_serializer(collectors, many=True)
        return Response(serializer.data)

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.select_related('species', 'collector__user').prefetch_related(
        'processing_events', 'quality_tests', 'verifications'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'quality_grade', 'harvesting_method', 'species', 'collector']
    search_fields = ['batch_id', 'species__name', 'collector__collector_id']
    ordering_fields = ['batch_id', 'created_at', 'collection_date', 'quantity_kg']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BatchCreateSerializer
        elif self.action == 'retrieve':
            return BatchDetailSerializer
        return BatchSerializer
    
    def get_permissions(self):
        """Allow public access to verify action"""
        if self.action == 'verify':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def verify(self, request, pk=None):
        """Public endpoint for consumer verification"""
        try:
            batch = self.get_object()
            
            # Record verification event
            consumer_location = None
            lat = request.query_params.get('lat')
            lng = request.query_params.get('lng')
            if lat and lng:
                consumer_location = Point(float(lng), float(lat), srid=4326)
            
            ConsumerVerification.objects.create(
                batch=batch,
                consumer_location=consumer_location,
                verification_method='BATCH_LOOKUP',
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            serializer = BatchDetailSerializer(batch)
            return Response(serializer.data)
            
        except Batch.DoesNotExist:
            return Response({'error': 'Batch not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get batch statistics and analytics"""
        # Date range filter
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.queryset.filter(created_at__gte=start_date)
        
        # Basic stats
        total_batches = queryset.count()
        total_quantity = queryset.aggregate(Sum('quantity_kg'))['quantity_kg__sum'] or 0
        
        # Species distribution
        species_dist = dict(
            queryset.values('species__name')
            .annotate(count=Count('batch_id'))
            .values_list('species__name', 'count')
        )
        
        # Quality distribution
        quality_dist = dict(
            queryset.values('quality_grade')
            .annotate(count=Count('batch_id'))
            .values_list('quality_grade', 'count')
        )
        
        # Status distribution
        status_dist = dict(
            queryset.values('status')
            .annotate(count=Count('batch_id'))
            .values_list('status', 'count')
        )
        
        # Monthly trend (last 12 months)
        monthly_trend = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=31)
            month_count = queryset.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            monthly_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'count': month_count
            })
        
        # Top collectors
        top_collectors = list(
            queryset.values('collector__collector_id', 'collector__user__first_name', 'collector__user__last_name')
            .annotate(batch_count=Count('batch_id'), total_quantity=Sum('quantity_kg'))
            .order_by('-batch_count')[:10]
        )
        
        # Sustainability metrics
        sustainability_metrics = {
            'avg_soil_health': queryset.aggregate(Avg('soil_health_score'))['soil_health_score__avg'] or 0,
            'sustainable_methods_percent': (
                queryset.filter(harvesting_method__in=['HAND_PICKED', 'SELECTIVE', 'SUSTAINABLE']).count() 
                / max(total_batches, 1) * 100
            ),
            'certified_collectors_percent': (
                queryset.filter(collector__certification_level__in=['CERTIFIED', 'PREMIUM']).count()
                / max(total_batches, 1) * 100
            )
        }
        
        stats_data = {
            'total_batches': total_batches,
            'total_quantity_kg': total_quantity,
            'species_distribution': species_dist,
            'quality_distribution': quality_dist,
            'status_distribution': status_dist,
            'monthly_collection_trend': monthly_trend,
            'top_collectors': top_collectors,
            'sustainability_metrics': sustainability_metrics
        }
        
        serializer = BatchStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby_collections(self, request):
        """Find batches collected near a location"""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = float(request.query_params.get('radius', 100))
        
        if not lat or not lng:
            return Response({'error': 'lat and lng parameters required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        point = Point(float(lng), float(lat), srid=4326)
        batches = self.queryset.filter(
            collection_location__distance_lte=(point, Distance(km=radius_km))
        ).annotate(
            distance=Distance('collection_location', point)
        ).order_by('distance')
        
        serializer = self.get_serializer(batches, many=True)
        return Response(serializer.data)

class ProcessingEventViewSet(viewsets.ModelViewSet):
    queryset = ProcessingEvent.objects.select_related('batch', 'processor')
    serializer_class = ProcessingEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'batch', 'processor']
    search_fields = ['batch__batch_id', 'facility_name', 'processor__username']
    ordering_fields = ['event_date', 'created_at']
    ordering = ['-event_date']

class QualityTestViewSet(viewsets.ModelViewSet):
    queryset = QualityTest.objects.select_related('batch')
    serializer_class = QualityTestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['test_type', 'pass_status', 'batch']
    search_fields = ['batch__batch_id', 'testing_lab', 'certificate_number']
    ordering_fields = ['test_date', 'created_at']
    ordering = ['-test_date']

class ConsumerVerificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConsumerVerification.objects.select_related('batch')
    serializer_class = ConsumerVerificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['verification_method', 'batch']
    ordering_fields = ['verification_date']
    ordering = ['-verification_date']
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get verification analytics"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.queryset.filter(verification_date__gte=start_date)
        
        analytics = {
            'total_verifications': queryset.count(),
            'unique_batches_verified': queryset.values('batch').distinct().count(),
            'verification_methods': dict(
                queryset.values('verification_method')
                .annotate(count=Count('id'))
                .values_list('verification_method', 'count')
            ),
            'daily_trend': []
        }
        
        # Daily verification trend
        for i in range(days):
            day = timezone.now().date() - timedelta(days=i)
            day_count = queryset.filter(verification_date__date=day).count()
            analytics['daily_trend'].append({
                'date': day.isoformat(),
                'count': day_count
            })
        
        return Response(analytics)
