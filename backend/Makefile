.PHONY: test test-fast test-coverage test-integration lint format install-dev migrate loaddata

# Development setup
install-dev:
	pip install -r requirements.txt
	python manage.py migrate
	python manage.py loaddata fixtures/initial_data.json

# Database operations
migrate:
	python manage.py makemigrations
	python manage.py migrate

loaddata:
	python manage.py loaddata fixtures/initial_data.json

# Testing
test:
	pytest

test-fast:
	pytest -x --ff

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term-missing

test-integration:
	pytest -m integration

# Code quality
lint:
	flake8 .
	black --check .
	isort --check-only .

format:
	black .
	isort .

# Performance testing
load-test:
	locust -f locustfile.py --host=http://localhost:8000

# API documentation
docs:
	python manage.py spectacular --color --file schema.yml
	echo "API documentation generated at schema.yml"
	echo "View interactive docs at http://localhost:8000/api/docs/"

# Development server
runserver:
	python manage.py runserver

# Celery workers
celery:
	celery -A herbtrace worker -l info

celery-beat:
	celery -A herbtrace beat -l info
