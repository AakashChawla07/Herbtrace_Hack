from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth.models import User
from .models import HerbSpecies, Collector, Batch, ProcessingEvent, QualityTest, ConsumerVerification
import qrcode
import io
import base64

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']

class HerbSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HerbSpecies
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class CollectorSerializer(GeoFeatureModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = HerbSpeciesSerializer(many=True, read_only=True)
    
    class Meta:
        model = Collector
        geo_field = 'location'
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class CollectorCreateSerializer(serializers.ModelSerializer):
    user_data = UserSerializer()
    
    class Meta:
        model = Collector
        fields = ['collector_id', 'phone_number', 'address', 'location', 
                 'certification_level', 'experience_years', 'user_data']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data')
        user = User.objects.create_user(**user_data)
        collector = Collector.objects.create(user=user, **validated_data)
        return collector

class BatchSerializer(GeoFeatureModelSerializer):
    species = HerbSpeciesSerializer(read_only=True)
    collector = CollectorSerializer(read_only=True)
    processing_events_count = serializers.SerializerMethodField()
    quality_tests_count = serializers.SerializerMethodField()
    verifications_count = serializers.SerializerMethodField()
    qr_code = serializers.SerializerMethodField()
    sustainability_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Batch
        geo_field = 'collection_location'
        fields = '__all__'
        read_only_fields = ['batch_id', 'blockchain_hash', 'is_blockchain_verified', 
                           'created_at', 'updated_at']
    
    def get_processing_events_count(self, obj):
        return obj.processing_events.count()
    
    def get_quality_tests_count(self, obj):
        return obj.quality_tests.count()
    
    def get_verifications_count(self, obj):
        return obj.verifications.count()
    
    def get_qr_code(self, obj):
        """Generate QR code for batch verification"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        verification_url = f"https://herbtrace.app/verify/{obj.batch_id}"
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def get_sustainability_score(self, obj):
        """Calculate sustainability score based on various factors"""
        score = 0
        
        # Harvesting method score
        method_scores = {
            'HAND_PICKED': 25,
            'SELECTIVE': 20,
            'SUSTAINABLE': 15,
            'TRADITIONAL': 10,
        }
        score += method_scores.get(obj.harvesting_method, 0)
        
        # Soil health score
        if obj.soil_health_score:
            score += obj.soil_health_score * 2.5
        
        # Regeneration time consideration
        if obj.regeneration_time_months:
            if obj.regeneration_time_months >= 12:
                score += 20
            elif obj.regeneration_time_months >= 6:
                score += 15
            else:
                score += 10
        
        # Quality grade bonus
        grade_scores = {'A+': 15, 'A': 12, 'B': 8, 'C': 5}
        score += grade_scores.get(obj.quality_grade, 0)
        
        # Certification level of collector
        cert_scores = {'PREMIUM': 15, 'CERTIFIED': 10, 'BASIC': 5}
        score += cert_scores.get(obj.collector.certification_level, 0)
        
        return min(100, max(0, score))

class BatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['species', 'collector', 'collection_date', 'collection_location',
                 'collection_area_hectares', 'altitude_meters', 'weather_conditions',
                 'quantity_kg', 'moisture_content', 'quality_grade', 'harvesting_method',
                 'regeneration_time_months', 'soil_health_score', 'collection_photos']

class ProcessingEventSerializer(GeoFeatureModelSerializer):
    processor = UserSerializer(read_only=True)
    batch_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcessingEvent
        geo_field = 'location'
        fields = '__all__'
        read_only_fields = ['blockchain_hash', 'is_blockchain_verified', 
                           'created_at', 'updated_at']
    
    def get_batch_info(self, obj):
        return {
            'batch_id': obj.batch.batch_id,
            'species': obj.batch.species.name,
            'collector': obj.batch.collector.collector_id
        }

class QualityTestSerializer(serializers.ModelSerializer):
    batch_info = serializers.SerializerMethodField()
    
    class Meta:
        model = QualityTest
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_batch_info(self, obj):
        return {
            'batch_id': obj.batch.batch_id,
            'species': obj.batch.species.name,
            'quality_grade': obj.batch.quality_grade
        }

class ConsumerVerificationSerializer(GeoFeatureModelSerializer):
    batch_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsumerVerification
        geo_field = 'consumer_location'
        fields = '__all__'
        read_only_fields = ['verification_date']
    
    def get_batch_info(self, obj):
        return {
            'batch_id': obj.batch.batch_id,
            'species': obj.batch.species.name,
            'collector': obj.batch.collector.collector_id,
            'status': obj.batch.status
        }

class BatchDetailSerializer(BatchSerializer):
    """Detailed batch serializer with all related data"""
    processing_events = ProcessingEventSerializer(many=True, read_only=True)
    quality_tests = QualityTestSerializer(many=True, read_only=True)
    recent_verifications = serializers.SerializerMethodField()
    supply_chain_timeline = serializers.SerializerMethodField()
    
    def get_recent_verifications(self, obj):
        recent = obj.verifications.order_by('-verification_date')[:10]
        return ConsumerVerificationSerializer(recent, many=True).data
    
    def get_supply_chain_timeline(self, obj):
        """Create a timeline of all events for this batch"""
        timeline = []
        
        # Collection event
        timeline.append({
            'date': obj.collection_date,
            'type': 'COLLECTION',
            'title': 'Herb Collection',
            'description': f'Collected {obj.quantity_kg}kg of {obj.species.name}',
            'location': {
                'lat': obj.collection_location.y,
                'lng': obj.collection_location.x
            } if obj.collection_location else None,
            'actor': obj.collector.user.get_full_name(),
            'details': {
                'quantity': str(obj.quantity_kg),
                'quality_grade': obj.quality_grade,
                'harvesting_method': obj.harvesting_method
            }
        })
        
        # Processing events
        for event in obj.processing_events.all():
            timeline.append({
                'date': event.event_date,
                'type': event.event_type,
                'title': event.get_event_type_display(),
                'description': f'{event.event_type.lower().replace("_", " ").title()} at {event.facility_name}',
                'location': {
                    'lat': event.location.y,
                    'lng': event.location.x
                } if event.location else None,
                'actor': event.processor.get_full_name(),
                'details': {
                    'facility': event.facility_name,
                    'input_quantity': str(event.input_quantity_kg),
                    'output_quantity': str(event.output_quantity_kg) if event.output_quantity_kg else None,
                    'yield_percentage': str(event.yield_percentage) if event.yield_percentage else None
                }
            })
        
        # Quality tests
        for test in obj.quality_tests.all():
            timeline.append({
                'date': test.test_date,
                'type': 'QUALITY_TEST',
                'title': f'{test.get_test_type_display()}',
                'description': f'Quality test at {test.testing_lab}',
                'location': None,
                'actor': test.testing_lab,
                'details': {
                    'test_type': test.test_type,
                    'pass_status': test.pass_status,
                    'lab': test.testing_lab,
                    'certificate': test.certificate_number
                }
            })
        
        # Sort timeline by date
        timeline.sort(key=lambda x: x['date'])
        return timeline

class BatchStatsSerializer(serializers.Serializer):
    """Serializer for batch statistics"""
    total_batches = serializers.IntegerField()
    total_quantity_kg = serializers.DecimalField(max_digits=15, decimal_places=3)
    species_distribution = serializers.DictField()
    quality_distribution = serializers.DictField()
    status_distribution = serializers.DictField()
    monthly_collection_trend = serializers.ListField()
    top_collectors = serializers.ListField()
    sustainability_metrics = serializers.DictField()
