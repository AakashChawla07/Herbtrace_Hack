# HerbTrace Backend - Django REST Framework

A blockchain-based Ayurvedic herb traceability system backend built with Django REST Framework.

## Setup Instructions

### 1. Create Virtual Environment
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

### 2. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Environment Variables
Create a `.env` file in the backend directory:
\`\`\`bash
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/herbtrace
REDIS_URL=redis://localhost:6379/0
BLOCKCHAIN_NETWORK_URL=http://localhost:8545
BLOCKCHAIN_PRIVATE_KEY=your-private-key
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
\`\`\`

### 4. Database Setup
\`\`\`bash
# Create database (PostgreSQL with PostGIS)
createdb herbtrace
psql herbtrace -c "CREATE EXTENSION postgis;"

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
\`\`\`

### 5. Load Initial Data
\`\`\`bash
python manage.py loaddata fixtures/herb_species.json
python manage.py loaddata fixtures/sample_data.json
\`\`\`

### 6. Run Development Server
\`\`\`bash
python manage.py runserver
\`\`\`

### 7. Start Celery Worker (for blockchain tasks)
\`\`\`bash
celery -A herbtrace worker -l info
\`\`\`

## API Documentation

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- API Schema: http://localhost:8000/api/schema/

## Testing

\`\`\`bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test tests.test_traceability

# Run with coverage
coverage run --source='.' manage.py test
coverage report
\`\`\`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - User logout

### Traceability
- `GET /api/batches/` - List all batches
- `POST /api/batches/` - Create new batch
- `GET /api/batches/{id}/` - Get batch details
- `GET /api/batches/{id}/verify/` - Verify batch authenticity
- `GET /api/batches/{id}/timeline/` - Get batch timeline

### Blockchain
- `GET /api/blockchain/transactions/` - List blockchain transactions
- `POST /api/blockchain/verify/` - Verify blockchain record
- `GET /api/blockchain/analytics/` - Blockchain analytics

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper database and Redis URLs
3. Set up SSL certificates
4. Configure web server (nginx/Apache)
5. Use gunicorn for WSGI server
6. Set up monitoring and logging
