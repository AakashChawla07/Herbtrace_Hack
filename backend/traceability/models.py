from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from datetime import datetime

class HerbSpecies(models.Model):
    """Ayurvedic herb species master data"""
    name = models.CharField(max_length=200, unique=True)
    scientific_name = models.CharField(max_length=200, blank=True)
    sanskrit_name = models.CharField(max_length=200, blank=True)
    common_names = models.JSONField(default=list, blank=True)
    medicinal_properties = models.JSONField(default=dict, blank=True)
    harvesting_season = models.CharField(max_length=100, blank=True)
    quality_parameters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Herb Species"

    def __str__(self):
        return f"{self.name} ({self.scientific_name})"

class Collector(models.Model):
    """Herb collectors/farmers profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    collector_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    location = gis_models.PointField(null=True, blank=True)
    certification_level = models.CharField(
        max_length=20,
        choices=[
            ('BASIC', 'Basic'),
            ('CERTIFIED', 'Certified Organic'),
            ('PREMIUM', 'Premium Ayurvedic'),
        ],
        default='BASIC'
    )
    experience_years = models.PositiveIntegerField(default=0)
    specializations = models.ManyToManyField(HerbSpecies, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.collector_id} - {self.user.get_full_name()}"

class Batch(models.Model):
    """Main batch entity for herb traceability"""
    batch_id = models.CharField(max_length=50, unique=True, primary_key=True)
    species = models.ForeignKey(HerbSpecies, on_delete=models.CASCADE)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    
    # Collection details
    collection_date = models.DateTimeField()
    collection_location = gis_models.PointField()
    collection_area_hectares = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    altitude_meters = models.IntegerField(null=True, blank=True)
    weather_conditions = models.JSONField(default=dict, blank=True)
    
    # Quantity and quality
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=3)
    moisture_content = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    quality_grade = models.CharField(
        max_length=10,
        choices=[
            ('A+', 'Premium'),
            ('A', 'High'),
            ('B', 'Standard'),
            ('C', 'Basic'),
        ],
        default='B'
    )
    
    # Sustainability metrics
    harvesting_method = models.CharField(
        max_length=50,
        choices=[
            ('HAND_PICKED', 'Hand Picked'),
            ('SELECTIVE', 'Selective Harvesting'),
            ('SUSTAINABLE', 'Sustainable Methods'),
            ('TRADITIONAL', 'Traditional Methods'),
        ],
        default='HAND_PICKED'
    )
    regeneration_time_months = models.PositiveIntegerField(null=True, blank=True)
    soil_health_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('COLLECTED', 'Collected'),
            ('PROCESSING', 'Processing'),
            ('QUALITY_CHECK', 'Quality Check'),
            ('PACKAGED', 'Packaged'),
            ('SHIPPED', 'Shipped'),
            ('DELIVERED', 'Delivered'),
        ],
        default='COLLECTED'
    )
    
    # Blockchain integration
    blockchain_hash = models.CharField(max_length=66, blank=True)
    is_blockchain_verified = models.BooleanField(default=False)
    
    # Media
    collection_photos = models.JSONField(default=list, blank=True)
    quality_certificates = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch {self.batch_id} - {self.species.name}"

    def save(self, *args, **kwargs):
        if not self.batch_id:
            # Generate unique batch ID
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            species_code = self.species.name[:3].upper()
            collector_code = self.collector.collector_id[-3:]
            self.batch_id = f"HT{species_code}{collector_code}{timestamp}"
        super().save(*args, **kwargs)

class ProcessingEvent(models.Model):
    """Processing events in the supply chain"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='processing_events')
    processor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    event_type = models.CharField(
        max_length=30,
        choices=[
            ('CLEANING', 'Cleaning'),
            ('DRYING', 'Drying'),
            ('GRINDING', 'Grinding'),
            ('EXTRACTION', 'Extraction'),
            ('PACKAGING', 'Packaging'),
            ('QUALITY_TEST', 'Quality Testing'),
            ('CERTIFICATION', 'Certification'),
        ]
    )
    
    event_date = models.DateTimeField()
    location = gis_models.PointField(null=True, blank=True)
    facility_name = models.CharField(max_length=200)
    
    # Processing parameters
    temperature_celsius = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    duration_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Quality metrics
    input_quantity_kg = models.DecimalField(max_digits=10, decimal_places=3)
    output_quantity_kg = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    yield_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Documentation
    process_notes = models.TextField(blank=True)
    quality_parameters = models.JSONField(default=dict, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    
    # Blockchain
    blockchain_hash = models.CharField(max_length=66, blank=True)
    is_blockchain_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return f"{self.event_type} - {self.batch.batch_id} on {self.event_date.date()}"

class QualityTest(models.Model):
    """Quality testing records"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='quality_tests')
    test_type = models.CharField(
        max_length=50,
        choices=[
            ('MOISTURE', 'Moisture Content'),
            ('PURITY', 'Purity Analysis'),
            ('POTENCY', 'Active Compound Potency'),
            ('CONTAMINATION', 'Contamination Check'),
            ('HEAVY_METALS', 'Heavy Metals'),
            ('PESTICIDES', 'Pesticide Residue'),
            ('MICROBIAL', 'Microbial Analysis'),
        ]
    )
    
    test_date = models.DateTimeField()
    testing_lab = models.CharField(max_length=200)
    lab_certification = models.CharField(max_length=100, blank=True)
    
    # Test results
    test_results = models.JSONField(default=dict)
    pass_status = models.BooleanField()
    compliance_standards = models.JSONField(default=list, blank=True)
    
    # Documentation
    test_report_url = models.URLField(blank=True)
    certificate_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_type} - {self.batch.batch_id} - {'PASS' if self.pass_status else 'FAIL'}"

class ConsumerVerification(models.Model):
    """Consumer verification events"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='verifications')
    verification_date = models.DateTimeField(auto_now_add=True)
    consumer_location = gis_models.PointField(null=True, blank=True)
    verification_method = models.CharField(
        max_length=20,
        choices=[
            ('QR_SCAN', 'QR Code Scan'),
            ('BATCH_LOOKUP', 'Batch ID Lookup'),
            ('NFC', 'NFC Tag'),
        ],
        default='QR_SCAN'
    )
    
    # Analytics
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"Verification - {self.batch.batch_id} on {self.verification_date.date()}"
