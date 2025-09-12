from rest_framework import serializers
from .models import BlockchainTransaction, SmartContract

class BlockchainTransactionSerializer(serializers.ModelSerializer):
    initiator_name = serializers.CharField(source='initiator.get_full_name', read_only=True)
    transaction_fee_eth = serializers.SerializerMethodField()
    confirmations = serializers.SerializerMethodField()
    
    class Meta:
        model = BlockchainTransaction
        fields = '__all__'
        read_only_fields = ['transaction_id', 'created_at', 'confirmed_at']
    
    def get_transaction_fee_eth(self, obj):
        if obj.transaction_fee:
            return float(obj.transaction_fee)
        return None
    
    def get_confirmations(self, obj):
        if obj.block_number and obj.status == 'CONFIRMED':
            # This would need to be calculated with current block number
            # For now, return a placeholder
            return 12  # Assuming 12+ confirmations for confirmed transactions
        return 0

class SmartContractSerializer(serializers.ModelSerializer):
    deployer_name = serializers.CharField(source='deployer.get_full_name', read_only=True)
    
    class Meta:
        model = SmartContract
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class BlockchainStatsSerializer(serializers.Serializer):
    """Serializer for blockchain statistics"""
    network_info = serializers.DictField()
    transaction_stats = serializers.DictField()
    cost_analytics = serializers.DictField()
    recent_transactions = BlockchainTransactionSerializer(many=True, read_only=True)
