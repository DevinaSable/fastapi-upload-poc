from locust import HttpUser, task, between
import json

class HealthUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def health_check(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


class UploadUser(HttpUser):
    wait_time = between(1, 3)
    token: str = ""

    def on_start(self):
        """Login once per simulated user before tasks run."""
        response = self.client.post("/auth/login", json={
            "username": "devd",
            "password": "secret123"
        })
        self.token = response.json()["access_token"]

    @task(1)
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def upload_file(self):
        self.client.post(
            "/files/upload",
            headers={"Authorization": f"Bearer {self.token}"},
            files={"file": ("test.pdf", b"mock pdf content", "application/pdf")},
        )