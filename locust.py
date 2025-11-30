from locust import HttpUser, task, between, LoadTestShape
import time
import csv
from statistics import mean

# Store request duration for analytics
REQUEST_LOG = []


class StudentUser(HttpUser):
    wait_time = between(1, 3)  # Simulates real user think-time

    @task
    def access_pages(self):
        start = time.time()
        with self.client.get("/", catch_response=True) as response:
            duration = (time.time() - start) * 1000
            REQUEST_LOG.append(duration)

        with self.client.get("/login/", catch_response=True):
            pass

        with self.client.get("/quiz/sample-quiz/", catch_response=True):
            pass


# Controls concurrency rise (0 → 500 users smoothly)
class StepLoadShape(LoadTestShape):
    stages = [
        {"users": 100, "duration": 30},
        {"users": 200, "duration": 60},
        {"users": 300, "duration": 90},
        {"users": 400, "duration": 120},
        {"users": 500, "duration": 150},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["users"])
        return None


def write_batch_analytics():
    batch_results = []
    step = 100
    for start in range(0, len(REQUEST_LOG), step):
        end = start + step
        batch = REQUEST_LOG[start:end]
        if not batch:
            continue
        batch_results.append(
            {
                "batch_range": f"{start+1}–{end}",
                "avg_response_ms": mean(batch),
                "max_response_ms": max(batch),
                "min_response_ms": min(batch)
            }
        )

    with open("batch_analytics.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=batch_results[0].keys())
        writer.writeheader()
        writer.writerows(batch_results)


# Save analytics on exit
import atexit
atexit.register(write_batch_analytics)
