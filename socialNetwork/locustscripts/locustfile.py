from locust import HttpUser, task, between
import locust.stats

class HelloWorldUser(HttpUser):
    
    # wait time after each performed task for each spawned user
    wait_time = between(0, 0.05)

    # url to index page
    host = "http://localhost:8080"
    
    locust.stats.CSV_STATS_INTERVAL_SEC = 1 # default is 1 second
    locust.stats.CSV_STATS_FLUSH_INTERVAL_SEC = 10 # Determines how often the data is flushed to disk, default is 10 seconds
    #http://localhost:8080/wrk2-api/user/register

    #loc10:
    #locust --csv=example --headless -t10s -u 100 -r 100 -f
    # Flushes data every 10 sec by default, test needs to run longer than that. 

    # 1: intra-service, 0: no intra-service.

    
    @task
    def hello_world(self):
        self.client.post("/wrk2-api/user/register", json={"intra_service": 0})
        
