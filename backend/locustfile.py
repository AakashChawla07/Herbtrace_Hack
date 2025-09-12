from locust import HttpUser, task, between
import random
import json

class HerbTraceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get authentication token"""
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def view_batch_list(self):
        """View batch list"""
        self.client.get("/api/v1/batches/")
    
    @task(2)
    def view_batch_detail(self):
        """View random batch detail"""
        batch_id = f"HT{random.randint(1000, 9999)}"
        self.client.get(f"/api/v1/batches/{batch_id}/")
    
    @task(1)
    def verify_batch(self):
        """Verify batch (public endpoint)"""
        batch_id = f"HT{random.randint(1000, 9999)}"
        self.client.get(f"/api/v1/batches/{batch_id}/verify/")
    
    @task(1)
    def view_batch_stats(self):
        """View batch statistics"""
        self.client.get("/api/v1/batches/stats/")
    
    @task(1)
    def search_nearby_batches(self):
        """Search for nearby batches"""
        lat = random.uniform(8.0, 37.0)
        lng = random.uniform(68.0, 97.0)
        self.client.get(f"/api/v1/batches/nearby-collections/?lat={lat}&lng={lng}&radius=100")
    
    @task(1)
    def view_blockchain_status(self):
        """Check blockchain status"""
        self.client.get("/api/v1/blockchain/status/")

class AdminUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login as admin"""
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "admin",
            "password": "adminpass123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(2)
    def create_batch(self):
        """Create new batch"""
        batch_data = {
            "species": 1,
            "collector": 1,
            "collection_date": "2024-01-15T10:00:00Z",
            "collection_location": {
                "type": "Point",
                "coordinates": [random.uniform(68.0, 97.0), random.uniform(8.0, 37.0)]
            },
            "quantity_kg": str(random.uniform(10.0, 100.0)),
            "quality_grade": random.choice(["A+", "A", "B", "C"]),
            "harvesting_method": random.choice(["HAND_PICKED", "SELECTIVE", "SUSTAINABLE"])
        }
        
        self.client.post("/api/v1/batches/", json=batch_data)
    
    @task(1)
    def view_blockchain_analytics(self):
        """View blockchain analytics"""
        self.client.get("/api/v1/blockchain/analytics/")
    
    @task(1)
    def view_blockchain_transactions(self):
        """View blockchain transactions"""
        self.client.get("/api/v1/blockchain/transactions/")
