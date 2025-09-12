import django_filters
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from .models import Batch, ProcessingEvent, QualityTest

class BatchFilter(django_filters.FilterSet):
    collection_date_from = django_filters.DateTimeFilter(field_name='collection_date', lookup_expr='gte')
    collection_date_to = django_filters.DateTimeFilter(field_name='collection_date', lookup_expr='lte')
    quantity_min = django_filters.NumberFilter(field_name='quantity_kg', lookup_expr='gte')
    quantity_max = django_filters.NumberFilter(field_name='quantity_kg', lookup_expr='lte')
    near_lat = django_filters.NumberFilter(method='filter_near_location')
    near_lng = django_filters.NumberFilter(method='filter_near_location')
    radius_km = django_filters.NumberFilter(method='filter_near_location')
    
    class Meta:
        model = Batch
        fields = ['status', 'quality_grade', 'harvesting_method', 'species', 'collector']
    
    def filter_near_location(self, queryset, name, value):
        lat = self.data.get('near_lat')
        lng = self.data.get('near_lng')
        radius = self.data.get('radius_km', 50)
        
        if lat and lng:
            point = Point(float(lng), float(lat), srid=4326)
            return queryset.filter(
                collection_location__distance_lte=(point, Distance(km=float(radius)))
            )
        return queryset

class ProcessingEventFilter(django_filters.FilterSet):
    event_date_from = django_filters.DateTimeFilter(field_name='event_date', lookup_expr='gte')
    event_date_to = django_filters.DateTimeFilter(field_name='event_date', lookup_expr='lte')
    
    class Meta:
        model = ProcessingEvent
        fields = ['event_type', 'batch', 'processor', 'is_blockchain_verified']

class QualityTestFilter(django_filters.FilterSet):
    test_date_from = django_filters.DateTimeFilter(field_name='test_date', lookup_expr='gte')
    test_date_to = django_filters.DateTimeFilter(field_name='test_date', lookup_expr='lte')
    
    class Meta:
        model = QualityTest
        fields = ['test_type', 'pass_status', 'batch', 'testing_lab']
