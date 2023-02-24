from locust import LoadTestShape
from locustfile import HelloWorldUser
from copy import deepcopy
import numpy as np
from math import ceil

TIME_UNITS = 1 / 5 
USER_NUM = 23

noise = lambda: np.random.normal(0, 5)

def transform(list_of_lists):
    out = []
    for sublist in list_of_lists:
        for item in sublist:
            out.append(item)
    out = [deepcopy(a) for a in out]

    acc = 1
    for item in out:
        item["duration"] = acc 
        item["spawn_rate"] = 1 if item["spawn_rate"] == 0 else item["spawn_rate"] * USER_NUM
    
        #item["users"] *= USER_NUM + (noise() * USER_NUM)
        n = (noise() * USER_NUM)

        item["users"] = (item["users"] * USER_NUM) + n
        item["spawn_rate"] += abs(n)
        acc = acc + 1
    return out


def create_frame(prev_frame, duration, users):
    user_count = abs(prev_frame["users"] - users)    
    out = []
    for i in range(round(duration * TIME_UNITS)):
        out.append({"duration": 1, "users": users, "spawn_rate": ceil(user_count / (duration * TIME_UNITS)), "user_classes": [HelloWorldUser]})
    return out

tmp2 = [ create_frame({"users": item[0]},item[1], item[2] ) for item in  
         [(0, 30, 40),
          (40, 30 ,45),
          (45, 90, 50),
          (50, 30, 45),
          (45, 60, 42),
          (42, 30, 35),
          (42, 30, 100), 
          (100, 30, 150),
          (150, 60, 150),
          (150, 60, 165),
          (165, 30, 168),
          (168, 60, 175),
          (175, 30, 168),
          (168, 60, 120),
          (120, 30, 145),
          (145, 60, 145),
          (145, 30, 115),
          (115, 240, 145),
          (145, 60, 90),
          (90, 60, 42),
          (42, 180, 42),
          (42, 120, 25),
          (25, 30, 50),


          #Saturday duration:
          (50, 30, 30),
          (30, 150, 40),
          (40, 240, 60),
          (60, 60, 80),
          (80, 30, 82),
          (82, 60, 75),
          (75, 60, 65),
          (65, 120, 72),
          (72, 30, 50),
          (50, 180, 50),
          (50, 300, 20),
          (20, 180, 15),

          # Sunday duration: 1440 min
          (15, 72, 45),
          (45, 72, 47),
          (47, 72, 45),
          (45, 72, 50),
          (50, 144, 60),
          (60, 72, 75),
          (75, 72, 70),
          (70, 72, 60),
          (60, 72, 55),
          (55, 72, 48),
          (48, 72, 48),
          (48, 72, 48),
          (48, 72, 22),
          (22, 72, 20),
          (20, 72, 24),
          (22, 72, 24),
          (24, 72, 25),
          (25, 72, 30),
          (30, 72, 50)
          
          #test 5 days
          #(50, 30, 40),
          #(40, 30 ,45),
          #(45, 90, 50),
          #(50, 30, 45),
          #(45, 60, 42),
          #(42, 30, 100), 
          #(100, 30, 150),
          #(150, 60, 150),
          #(150, 60, 165),
          #(165, 30, 168),
          #(168, 30, 175),
          #(175, 30, 168),
          #(168, 30, 120),
          #(120, 30, 145),
          #(145, 30, 145),
          #(145, 30, 115),
          #(115, 240, 145),
          #(145, 60, 90),
          #(90, 60, 42),
          #(42, 180, 42),
          #(42, 120, 25),
          #(25, 30, 50),
          #
          #(50, 30, 40),
          #(40, 30 ,45),
          #(45, 90, 50),
          #(50, 30, 45),
          #(45, 60, 42),
          #(42, 30, 100), 
          #(100, 30, 150),
          #(150, 60, 150),
          #(150, 60, 165),
          #(165, 30, 168),
          #(168, 30, 175),
          #(175, 30, 168),
          #(168, 30, 120),
          #(120, 30, 145),
          #(145, 30, 145),
          #(145, 30, 115),
          #(115, 240, 145),
          #(145, 60, 90),
          #(90, 60, 42),
          #(42, 180, 42),
          #(42, 120, 25),
          #(25, 30, 50),
          #
          #(50, 30, 40),
          #(40, 30 ,45),
          #(45, 90, 50),
          #(50, 30, 45),
          #(45, 60, 42),
          #(42, 30, 100), 
          #(100, 30, 150),
          #(150, 60, 150),
          #(150, 60, 165),
          #(165, 30, 168),
          #(168, 30, 175),
          #(175, 30, 168),
          #(168, 30, 120),
          #(120, 30, 145),
          #(145, 30, 145),
          #(145, 30, 115),
          #(115, 240, 145),
          #(145, 60, 90),
          #(90, 60, 42),
          #(42, 180, 42),
          #(42, 120, 25),
          #(25, 30, 50),
          #
          #(50, 30, 40),
          #(40, 30 ,45),
          #(45, 90, 50),
          #(50, 30, 45),
          #(45, 60, 42),
          #(42, 30, 100), 
          #(100, 30, 150),
          #(150, 60, 150),
          #(150, 60, 165),
          #(165, 30, 168),
          #(168, 30, 175),
          #(175, 30, 168),
          #(168, 30, 120),
          #(120, 30, 145),
          #(145, 30, 145),
          #(145, 30, 115),
          #(115, 240, 145),
          #(145, 60, 90),
          #(90, 60, 42),
          #(42, 180, 42),
          #(42, 120, 25),
          #(25, 30, 50)
          ]
    ]

class StagesShapeWithCustomUsers(LoadTestShape):

    noise = lambda: np.random.normal(0, 10)

    stages = transform(tmp2)


    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                try:
                    tick_data = (stage["users"], stage["spawn_rate"], stage["user_classes"])
                except:
                    tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None