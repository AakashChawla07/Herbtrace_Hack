from django.urls import path
from . import views

urlpatterns = [
    # Blockchain transactions
    path('api/v1/blockchain/transactions/', views.BlockchainTransactionListView.as_view(), name='blockchain_transactions'),
    path('api/v1/blockchain/transactions/<str:transaction_hash>/', views.BlockchainTransactionDetailView.as_view(), name='blockchain_transaction_detail'),
    
    # Smart contracts
    path('api/v1/blockchain/contracts/', views.SmartContractListView.as_view(), name='smart_contracts'),
    
    # Blockchain status and analytics
    path('api/v1/blockchain/status/', views.blockchain_status, name='blockchain_status'),
    path('api/v1/blockchain/analytics/', views.blockchain_analytics, name='blockchain_analytics'),
    
    # Verification and integrity
    path('api/v1/blockchain/verify/<str:batch_id>/', views.verify_batch_integrity, name='verify_batch_integrity'),
    path('api/v1/blockchain/transaction-status/<str:tx_hash>/', views.transaction_status, name='transaction_status'),
    
    # Manual operations
    path('api/v1/blockchain/sync/<str:batch_id>/', views.force_blockchain_sync, name='force_blockchain_sync'),
]
