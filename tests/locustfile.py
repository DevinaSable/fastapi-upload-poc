from locust import HttpUser, task, between


class HealthUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def health_check(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")