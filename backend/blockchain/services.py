from web3 import Web3
from eth_account import Account
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List

from .models import BlockchainTransaction, SmartContract
from traceability.models import Batch, ProcessingEvent, QualityTest

logger = logging.getLogger(__name__)

class BlockchainService:
    """Main blockchain service for HerbTrace"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_CONFIG['NETWORK_URL']))
        self.private_key = settings.BLOCKCHAIN_CONFIG['PRIVATE_KEY']
        self.account = Account.from_key(self.private_key) if self.private_key else None
        self.gas_limit = settings.BLOCKCHAIN_CONFIG['GAS_LIMIT']
        
        # Load smart contracts
        self.contracts = self._load_contracts()
    
    def _load_contracts(self) -> Dict[str, Any]:
        """Load smart contract instances"""
        contracts = {}
        
        try:
            # Load HerbTrace main contract
            main_contract = SmartContract.objects.get(name='HerbTraceMain', is_active=True)
            contracts['main'] = self.w3.eth.contract(
                address=main_contract.contract_address,
                abi=main_contract.abi
            )
            
            # Load Quality Assurance contract
            qa_contract = SmartContract.objects.get(name='QualityAssurance', is_active=True)
            contracts['quality'] = self.w3.eth.contract(
                address=qa_contract.contract_address,
                abi=qa_contract.abi
            )
            
        except SmartContract.DoesNotExist:
            logger.warning("Smart contracts not found in database")
        
        return contracts
    
    def is_connected(self) -> bool:
        """Check if connected to blockchain network"""
        try:
            return self.w3.is_connected()
        except Exception as e:
            logger.error(f"Blockchain connection error: {e}")
            return False
    
    def get_gas_price(self) -> int:
        """Get current gas price"""
        try:
            return self.w3.eth.gas_price
        except Exception as e:
            logger.error(f"Error getting gas price: {e}")
            return 20000000000  # 20 Gwei fallback
    
    def create_batch_hash(self, batch: Batch) -> str:
        """Create deterministic hash for batch data"""
        batch_data = {
            'batch_id': batch.batch_id,
            'species': batch.species.name,
            'collector': batch.collector.collector_id,
            'collection_date': batch.collection_date.isoformat(),
            'location': {
                'lat': float(batch.collection_location.y),
                'lng': float(batch.collection_location.x)
            } if batch.collection_location else None,
            'quantity_kg': str(batch.quantity_kg),
            'quality_grade': batch.quality_grade,
            'harvesting_method': batch.harvesting_method
        }
        
        batch_json = json.dumps(batch_data, sort_keys=True)
        return hashlib.sha256(batch_json.encode()).hexdigest()
    
    def record_collection_event(self, batch: Batch) -> Optional[str]:
        """Record collection event on blockchain"""
        if not self.is_connected() or 'main' not in self.contracts:
            logger.error("Blockchain not available for collection recording")
            return None
        
        try:
            contract = self.contracts['main']
            batch_hash = self.create_batch_hash(batch)
            
            # Prepare transaction data
            location_data = [0, 0]  # Default coordinates
            if batch.collection_location:
                # Convert to integer coordinates (multiply by 1e6 for precision)
                location_data = [
                    int(batch.collection_location.y * 1000000),
                    int(batch.collection_location.x * 1000000)
                ]
            
            # Build transaction
            transaction = contract.functions.recordCollection(
                batch.batch_id,
                batch_hash,
                batch.species.name,
                batch.collector.collector_id,
                int(batch.collection_date.timestamp()),
                location_data,
                int(batch.quantity_kg * 1000),  # Convert to grams
                batch.quality_grade,
                batch.harvesting_method
            ).build_transaction({
                'from': self.account.address,
                'gas': self.gas_limit,
                'gasPrice': self.get_gas_price(),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Record transaction in database
            blockchain_tx = BlockchainTransaction.objects.create(
                transaction_hash=tx_hash.hex(),
                transaction_type='COLLECTION',
                batch_id=batch.batch_id,
                initiator=batch.collector.user,
                contract_address=contract.address,
                gas_used=transaction['gas'],
                gas_price=transaction['gasPrice'],
                transaction_data={
                    'batch_hash': batch_hash,
                    'species': batch.species.name,
                    'collector': batch.collector.collector_id,
                    'location': location_data,
                    'quantity_grams': int(batch.quantity_kg * 1000),
                    'quality_grade': batch.quality_grade
                },
                status='PENDING'
            )
            
            logger.info(f"Collection event recorded for batch {batch.batch_id}: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error recording collection event: {e}")
            return None
    
    def record_processing_event(self, processing_event: ProcessingEvent) -> Optional[str]:
        """Record processing event on blockchain"""
        if not self.is_connected() or 'main' not in self.contracts:
            logger.error("Blockchain not available for processing recording")
            return None
        
        try:
            contract = self.contracts['main']
            
            # Create event hash
            event_data = {
                'batch_id': processing_event.batch.batch_id,
                'event_type': processing_event.event_type,
                'processor': processing_event.processor.username,
                'event_date': processing_event.event_date.isoformat(),
                'facility': processing_event.facility_name,
                'input_quantity': str(processing_event.input_quantity_kg),
                'output_quantity': str(processing_event.output_quantity_kg) if processing_event.output_quantity_kg else None
            }
            event_json = json.dumps(event_data, sort_keys=True)
            event_hash = hashlib.sha256(event_json.encode()).hexdigest()
            
            # Build transaction
            transaction = contract.functions.recordProcessing(
                processing_event.batch.batch_id,
                event_hash,
                processing_event.event_type,
                processing_event.processor.username,
                int(processing_event.event_date.timestamp()),
                processing_event.facility_name,
                int(processing_event.input_quantity_kg * 1000),  # Convert to grams
                int(processing_event.output_quantity_kg * 1000) if processing_event.output_quantity_kg else 0
            ).build_transaction({
                'from': self.account.address,
                'gas': self.gas_limit,
                'gasPrice': self.get_gas_price(),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Record transaction in database
            blockchain_tx = BlockchainTransaction.objects.create(
                transaction_hash=tx_hash.hex(),
                transaction_type='PROCESSING',
                batch_id=processing_event.batch.batch_id,
                initiator=processing_event.processor,
                contract_address=contract.address,
                gas_used=transaction['gas'],
                gas_price=transaction['gasPrice'],
                transaction_data=event_data,
                status='PENDING'
            )
            
            logger.info(f"Processing event recorded for batch {processing_event.batch.batch_id}: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error recording processing event: {e}")
            return None
    
    def record_quality_test(self, quality_test: QualityTest) -> Optional[str]:
        """Record quality test on blockchain"""
        if not self.is_connected() or 'quality' not in self.contracts:
            logger.error("Blockchain not available for quality test recording")
            return None
        
        try:
            contract = self.contracts['quality']
            
            # Create test hash
            test_data = {
                'batch_id': quality_test.batch.batch_id,
                'test_type': quality_test.test_type,
                'test_date': quality_test.test_date.isoformat(),
                'testing_lab': quality_test.testing_lab,
                'pass_status': quality_test.pass_status,
                'test_results': quality_test.test_results
            }
            test_json = json.dumps(test_data, sort_keys=True)
            test_hash = hashlib.sha256(test_json.encode()).hexdigest()
            
            # Build transaction
            transaction = contract.functions.recordQualityTest(
                quality_test.batch.batch_id,
                test_hash,
                quality_test.test_type,
                int(quality_test.test_date.timestamp()),
                quality_test.testing_lab,
                quality_test.pass_status,
                quality_test.certificate_number or ""
            ).build_transaction({
                'from': self.account.address,
                'gas': self.gas_limit,
                'gasPrice': self.get_gas_price(),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Record transaction in database
            blockchain_tx = BlockchainTransaction.objects.create(
                transaction_hash=tx_hash.hex(),
                transaction_type='QUALITY_TEST',
                batch_id=quality_test.batch.batch_id,
                initiator_id=1,  # System user for quality tests
                contract_address=contract.address,
                gas_used=transaction['gas'],
                gas_price=transaction['gasPrice'],
                transaction_data=test_data,
                status='PENDING'
            )
            
            logger.info(f"Quality test recorded for batch {quality_test.batch.batch_id}: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error recording quality test: {e}")
            return None
    
    def verify_batch_integrity(self, batch: Batch) -> Dict[str, Any]:
        """Verify batch data integrity against blockchain"""
        if not self.is_connected() or 'main' not in self.contracts:
            return {'verified': False, 'error': 'Blockchain not available'}
        
        try:
            contract = self.contracts['main']
            
            # Get batch data from blockchain
            batch_data = contract.functions.getBatch(batch.batch_id).call()
            
            if not batch_data or batch_data[0] == '':  # Empty batch ID means not found
                return {'verified': False, 'error': 'Batch not found on blockchain'}
            
            # Verify hash
            current_hash = self.create_batch_hash(batch)
            blockchain_hash = batch_data[1]  # Assuming hash is second field
            
            verification_result = {
                'verified': current_hash == blockchain_hash,
                'current_hash': current_hash,
                'blockchain_hash': blockchain_hash,
                'blockchain_data': {
                    'batch_id': batch_data[0],
                    'species': batch_data[2],
                    'collector': batch_data[3],
                    'timestamp': batch_data[4],
                    'location': batch_data[5],
                    'quantity_grams': batch_data[6],
                    'quality_grade': batch_data[7]
                }
            }
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Error verifying batch integrity: {e}")
            return {'verified': False, 'error': str(e)}
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction status and details"""
        try:
            # Get transaction receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            transaction = self.w3.eth.get_transaction(tx_hash)
            
            status_info = {
                'status': 'CONFIRMED' if receipt['status'] == 1 else 'FAILED',
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'gas_price': transaction['gasPrice'],
                'transaction_fee': Decimal(receipt['gasUsed'] * transaction['gasPrice']) / Decimal(10**18),
                'confirmations': self.w3.eth.block_number - receipt['blockNumber']
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            return {'status': 'PENDING', 'error': str(e)}
    
    def get_blockchain_analytics(self) -> Dict[str, Any]:
        """Get blockchain analytics and statistics"""
        try:
            # Get network info
            latest_block = self.w3.eth.block_number
            gas_price = self.get_gas_price()
            
            # Get transaction statistics
            total_transactions = BlockchainTransaction.objects.count()
            confirmed_transactions = BlockchainTransaction.objects.filter(status='CONFIRMED').count()
            pending_transactions = BlockchainTransaction.objects.filter(status='PENDING').count()
            failed_transactions = BlockchainTransaction.objects.filter(status='FAILED').count()
            
            # Calculate total fees
            total_fees = BlockchainTransaction.objects.filter(
                status='CONFIRMED'
            ).aggregate(
                total=models.Sum('transaction_fee')
            )['total'] or Decimal('0')
            
            analytics = {
                'network_info': {
                    'latest_block': latest_block,
                    'gas_price_gwei': gas_price / 10**9,
                    'connected': self.is_connected()
                },
                'transaction_stats': {
                    'total_transactions': total_transactions,
                    'confirmed_transactions': confirmed_transactions,
                    'pending_transactions': pending_transactions,
                    'failed_transactions': failed_transactions,
                    'success_rate': (confirmed_transactions / max(total_transactions, 1)) * 100
                },
                'cost_analytics': {
                    'total_fees_eth': float(total_fees),
                    'average_fee_eth': float(total_fees / max(confirmed_transactions, 1))
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting blockchain analytics: {e}")
            return {'error': str(e)}

# Global blockchain service instance
blockchain_service = BlockchainService()
