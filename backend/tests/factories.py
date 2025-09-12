import factory
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta
import random

from traceability.models import HerbSpecies, Collector, Batch, ProcessingEvent, QualityTest
from blockchain.models import BlockchainTransaction, SmartContract

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    user_type = 'COLLECTOR'
    is_verified = True
    phone_number = factory.Faker('phone_number')
    organization = factory.Faker('company')

class HerbSpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HerbSpecies
    
    name = factory.Faker('word')
    scientific_name = factory.LazyAttribute(lambda obj: f'{obj.name.title()} officinalis')
    sanskrit_name = factory.Faker('word')
    common_names = factory.LazyFunction(lambda: [factory.Faker('word').generate(), factory.Faker('word').generate()])
    medicinal_properties = factory.LazyFunction(lambda: {
        'anti_inflammatory': random.choice([True, False]),
        'antioxidant': random.choice([True, False]),
        'digestive': random.choice([True, False])
    })
    harvesting_season = factory.Faker('random_element', elements=['Spring', 'Summer', 'Monsoon', 'Winter'])
    quality_parameters = factory.LazyFunction(lambda: {
        'moisture': 'max 10%',
        'active_compound': 'min 3%'
    })

class CollectorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collector
    
    user = factory.SubFactory(UserFactory, user_type='COLLECTOR')
    collector_id = factory.Sequence(lambda n: f'COL{n:04d}')
    phone_number = factory.Faker('phone_number')
    address = factory.Faker('address')
    location = factory.LazyFunction(lambda: Point(
        random.uniform(68.0, 97.0),  # India longitude range
        random.uniform(8.0, 37.0),   # India latitude range
        srid=4326
    ))
    certification_level = factory.Faker('random_element', elements=['BASIC', 'CERTIFIED', 'PREMIUM'])
    experience_years = factory.Faker('random_int', min=1, max=30)
    is_verified = True

class BatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Batch
    
    species = factory.SubFactory(HerbSpeciesFactory)
    collector = factory.SubFactory(CollectorFactory)
    collection_date = factory.Faker('date_time_between', start_date='-30d', end_date='now', tzinfo=timezone.utc)
    collection_location = factory.LazyFunction(lambda: Point(
        random.uniform(68.0, 97.0),
        random.uniform(8.0, 37.0),
        srid=4326
    ))
    collection_area_hectares = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    altitude_meters = factory.Faker('random_int', min=100, max=3000)
    weather_conditions = factory.LazyFunction(lambda: {
        'temperature': random.randint(20, 35),
        'humidity': random.randint(40, 80),
        'rainfall': random.choice(['None', 'Light', 'Moderate'])
    })
    quantity_kg = factory.Faker('pydecimal', left_digits=4, right_digits=3, positive=True)
    moisture_content = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    quality_grade = factory.Faker('random_element', elements=['A+', 'A', 'B', 'C'])
    harvesting_method = factory.Faker('random_element', elements=['HAND_PICKED', 'SELECTIVE', 'SUSTAINABLE', 'TRADITIONAL'])
    regeneration_time_months = factory.Faker('random_int', min=6, max=24)
    soil_health_score = factory.Faker('random_int', min=1, max=10)
    status = 'COLLECTED'

class ProcessingEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProcessingEvent
    
    batch = factory.SubFactory(BatchFactory)
    processor = factory.SubFactory(UserFactory, user_type='PROCESSOR')
    event_type = factory.Faker('random_element', elements=['CLEANING', 'DRYING', 'GRINDING', 'EXTRACTION', 'PACKAGING'])
    event_date = factory.LazyAttribute(lambda obj: obj.batch.collection_date + timedelta(days=random.randint(1, 7)))
    location = factory.LazyFunction(lambda: Point(
        random.uniform(68.0, 97.0),
        random.uniform(8.0, 37.0),
        srid=4326
    ))
    facility_name = factory.Faker('company')
    temperature_celsius = factory.Faker('pydecimal', left_digits=2, right_digits=1, positive=True)
    humidity_percent = factory.Faker('pydecimal', left_digits=2, right_digits=1, positive=True)
    duration_hours = factory.Faker('pydecimal', left_digits=2, right_digits=1, positive=True)
    input_quantity_kg = factory.LazyAttribute(lambda obj: obj.batch.quantity_kg)
    output_quantity_kg = factory.LazyAttribute(lambda obj: obj.input_quantity_kg * random.uniform(0.7, 0.95))
    yield_percentage = factory.LazyAttribute(lambda obj: (obj.output_quantity_kg / obj.input_quantity_kg) * 100)

class QualityTestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QualityTest
    
    batch = factory.SubFactory(BatchFactory)
    test_type = factory.Faker('random_element', elements=['MOISTURE', 'PURITY', 'POTENCY', 'CONTAMINATION'])
    test_date = factory.LazyAttribute(lambda obj: obj.batch.collection_date + timedelta(days=random.randint(1, 10)))
    testing_lab = factory.Faker('company')
    lab_certification = factory.Faker('random_element', elements=['ISO 17025', 'NABL', 'FDA'])
    test_results = factory.LazyFunction(lambda: {
        'moisture_content': f'{random.uniform(5, 12):.2f}%',
        'purity': f'{random.uniform(85, 99):.1f}%',
        'active_compound': f'{random.uniform(2, 8):.2f}%'
    })
    pass_status = factory.Faker('boolean', chance_of_getting_true=85)
    certificate_number = factory.Faker('bothify', text='CERT-####-????')

class BlockchainTransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BlockchainTransaction
    
    transaction_hash = factory.Faker('sha256')
    transaction_type = factory.Faker('random_element', elements=['COLLECTION', 'PROCESSING', 'QUALITY_TEST'])
    batch_id = factory.LazyAttribute(lambda obj: f'HT{random.randint(1000, 9999)}')
    initiator = factory.SubFactory(UserFactory)
    contract_address = factory.Faker('bothify', text='0x########################################')
    gas_used = factory.Faker('random_int', min=21000, max=500000)
    gas_price = factory.Faker('random_int', min=1000000000, max=50000000000)
    status = 'CONFIRMED'
    transaction_data = factory.LazyFunction(lambda: {
        'timestamp': timezone.now().isoformat(),
        'data_hash': factory.Faker('sha256').generate()
    })

class SmartContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SmartContract
    
    name = factory.Faker('word')
    contract_address = factory.Faker('bothify', text='0x########################################')
    abi = factory.LazyFunction(lambda: [
        {
            "inputs": [],
            "name": "test",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ])
    version = factory.Faker('random_element', elements=['1.0.0', '1.1.0', '2.0.0'])
    description = factory.Faker('sentence')
    deployment_date = factory.Faker('date_time_between', start_date='-90d', end_date='now', tzinfo=timezone.utc)
    deployer = factory.SubFactory(UserFactory, user_type='ADMIN')
    is_active = True
