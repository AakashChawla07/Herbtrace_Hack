from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import HerbSpecies, Collector, Batch, ProcessingEvent, QualityTest, ConsumerVerification

@admin.register(HerbSpecies)
class HerbSpeciesAdmin(admin.ModelAdmin):
    list_display = ['name', 'scientific_name', 'sanskrit_name', 'created_at']
    search_fields = ['name', 'scientific_name', 'sanskrit_name']
    list_filter = ['created_at']

@admin.register(Collector)
class CollectorAdmin(OSMGeoAdmin):
    list_display = ['collector_id', 'user', 'certification_level', 'is_verified', 'created_at']
    list_filter = ['certification_level', 'is_verified', 'created_at']
    search_fields = ['collector_id', 'user__username', 'user__first_name', 'user__last_name']
    filter_horizontal = ['specializations']

@admin.register(Batch)
class BatchAdmin(OSMGeoAdmin):
    list_display = ['batch_id', 'species', 'collector', 'status', 'quantity_kg', 'quality_grade', 'created_at']
    list_filter = ['status', 'quality_grade', 'harvesting_method', 'is_blockchain_verified', 'created_at']
    search_fields = ['batch_id', 'species__name', 'collector__collector_id']
    readonly_fields = ['batch_id', 'blockchain_hash', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('batch_id', 'species', 'collector', 'status')
        }),
        ('Collection Details', {
            'fields': ('collection_date', 'collection_location', 'collection_area_hectares', 
                      'altitude_meters', 'weather_conditions')
        }),
        ('Quantity & Quality', {
            'fields': ('quantity_kg', 'moisture_content', 'quality_grade')
        }),
        ('Sustainability', {
            'fields': ('harvesting_method', 'regeneration_time_months', 'soil_health_score')
        }),
        ('Blockchain', {
            'fields': ('blockchain_hash', 'is_blockchain_verified')
        }),
        ('Media', {
            'fields': ('collection_photos', 'quality_certificates')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProcessingEvent)
class ProcessingEventAdmin(OSMGeoAdmin):
    list_display = ['batch', 'event_type', 'processor', 'event_date', 'facility_name', 'is_blockchain_verified']
    list_filter = ['event_type', 'is_blockchain_verified', 'event_date']
    search_fields = ['batch__batch_id', 'processor__username', 'facility_name']

@admin.register(QualityTest)
class QualityTestAdmin(admin.ModelAdmin):
    list_display = ['batch', 'test_type', 'test_date', 'testing_lab', 'pass_status']
    list_filter = ['test_type', 'pass_status', 'test_date']
    search_fields = ['batch__batch_id', 'testing_lab', 'certificate_number']

@admin.register(ConsumerVerification)
class ConsumerVerificationAdmin(OSMGeoAdmin):
    list_display = ['batch', 'verification_date', 'verification_method']
    list_filter = ['verification_method', 'verification_date']
    search_fields = ['batch__batch_id']
    readonly_fields = ['verification_date', 'user_agent', 'ip_address']
