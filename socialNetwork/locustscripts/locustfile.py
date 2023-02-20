import locust.stats
import gevent

from locust import HttpUser, task, between, events
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, MasterRunner, WorkerRunner

from time import sleep

"""
{
    serviceA: { 
        groupA : {instanceA: 15, instanceB : 13},
        groupB : {instanceA: 15, instanceB : 13},
        groupC : {instanceA: 15, instanceB : 13},
        groupD : {instanceA: 15, instanceB : 13},
        groupE : {instanceA: 15, instanceB : 13}
    },
    serviceB: ...
}

{intra_service_instances: "A,B", workout_duration: 34}

"""

client_assignments = {}
current_state =  {}

def update_state_master(environment, **kwargs):
    while True:
        environment.runner.send_message("update_state", current_state)
        gevent.sleep(1)

def update_state_worker(msg, **kwargs):
    global current_state
    current_state = msg.data

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if isinstance(environment.runner, MasterRunner):
        environment.runner.greenlet.spawn(lambda: update_state_master(environment))
    if isinstance(environment.runner, WorkerRunner):
        environment.runner.register_message("update_state", update_state_worker)

@events.worker_report.add_listener
def on_worker_report(client_id, data):
    global current_state, client_assignments
    for service, groups in data["client_assignments"].items():
        if not service in current_state:
            current_state[service] = {}

        for  group_id, instance in groups.items():
            if not group_id in current_state[service]:
                current_state[service][group_id] = {}

            for instance_id, num in instance.items():
                if not instance_id in current_state[service][group_id]:
                    current_state[service][group_id][instance_id] = 0


                current_state[service][group_id][instance_id] += num

@events.report_to_master.add_listener
def on_report_to_master(client_id, data):
    global client_assignments
    '''
        Data sent from worker to master
    '''
    data["client_assignments"] = client_assignments 
    client_assignments = {}

def save_assignment(assignment):
    global client_assignments
    assigned_instance = assignment.text.strip()
    if not "UserService" in client_assignments:
        client_assignments["UserService"] = {}

    if not "0" in client_assignments["UserService"]:
        client_assignments["UserService"]["0"] = {}
        
    if not assigned_instance in client_assignments["UserService"]["0"]:
        client_assignments["UserService"]["0"][assigned_instance] = 0
        
    client_assignments["UserService"]["0"][assigned_instance] += 1


class HelloWorldUser(HttpUser):
    
    # wait time after each performed task for each spawned user -> request per second per user
    wait_time = between(0, 0.05)

    # url to index page
    host = "http://localhost:8080"
    
    locust.stats.CSV_STATS_INTERVAL_SEC = 5 # default is 1 second
    locust.stats.CSV_STATS_FLUSH_INTERVAL_SEC = 10 # Determines how often the data is flushed to disk, default is 10 seconds
    #http://localhost:8080/wrk2-api/user/register

    #loc10:
    #locust --csv=example --headless -t10s -u 100 -r 100 -f
    # Flushes data every 10 sec by default, test needs to run longer than that. 

    # 1: intra-service, 0: no intra-service.
    
    @task
    def hello_world(self):
        json_data = {"intra_service": 0}


        res = self.client.post("/wrk2-api/user/register", json=json_data)
        save_assignment(res)
