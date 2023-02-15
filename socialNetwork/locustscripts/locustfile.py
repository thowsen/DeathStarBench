from locust import HttpUser, task, between
import locust.stats

class HelloWorldUser(HttpUser):
    
    # wait time after each performed task for each spawned user
    wait_time = between(0, 0.25)

    # url to index page
    host = "http://localhost:8080"

    locust.stats.CSV_STATS_INTERVAL_SEC = 5 # default is 1 second
    #locust.stats.CSV_STATS_FLUSH_INTERVAL_SEC = 60 # Determines how often the data is flushed to disk, default is 10 seconds

    @task
    def hello_world(self):
        self.client.get("/")
        
    