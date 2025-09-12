from django.db import models
from django.contrib.auth.models import User
import uuid

class BlockchainTransaction(models.Model):
    """Blockchain transaction records"""
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    transaction_hash = models.CharField(max_length=66, unique=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=30,
        choices=[
            ('COLLECTION', 'Collection Event'),
            ('PROCESSING', 'Processing Event'),
            ('QUALITY_TEST', 'Quality Test'),
            ('TRANSFER', 'Ownership Transfer'),
            ('VERIFICATION', 'Consumer Verification'),
        ]
    )
    
    # Related entities
    batch_id = models.CharField(max_length=50)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_transactions')
    
    # Blockchain data
    contract_address = models.CharField(max_length=42)
    gas_used = models.BigIntegerField(null=True, blank=True)
    gas_price = models.BigIntegerField(null=True, blank=True)
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    
    # Data payload
    transaction_data = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.batch_id} - {self.status}"

class SmartContract(models.Model):
    """Smart contract registry"""
    name = models.CharField(max_length=100, unique=True)
    contract_address = models.CharField(max_length=42, unique=True)
    abi = models.JSONField()
    bytecode = models.TextField(blank=True)
    
    # Contract metadata
    version = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    deployment_date = models.DateTimeField()
    deployer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version}"
