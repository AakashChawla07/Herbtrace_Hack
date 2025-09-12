from django.contrib import admin
from .models import BlockchainTransaction, SmartContract

@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'transaction_type', 'batch_id', 'status', 'initiator', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['transaction_hash', 'batch_id', 'initiator__username']
    readonly_fields = ['transaction_id', 'transaction_hash', 'block_number', 'created_at', 'confirmed_at']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('transaction_id', 'transaction_hash', 'transaction_type', 'batch_id', 'initiator')
        }),
        ('Blockchain Details', {
            'fields': ('contract_address', 'block_number', 'gas_used', 'gas_price', 'transaction_fee')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'confirmed_at')
        }),
        ('Data', {
            'fields': ('transaction_data',),
            'classes': ('collapse',)
        }),
    )

@admin.register(SmartContract)
class SmartContractAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'contract_address', 'is_active', 'deployment_date']
    list_filter = ['is_active', 'deployment_date']
    search_fields = ['name', 'contract_address', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contract Info', {
            'fields': ('name', 'version', 'description', 'contract_address')
        }),
        ('Deployment', {
            'fields': ('deployment_date', 'deployer', 'is_active')
        }),
        ('Technical', {
            'fields': ('abi', 'bytecode'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
