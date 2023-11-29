# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 14:03:36 2023

@author: wy448
"""

import threading as th
import time
stop = False

def fun1():
    global stop
    while True and not stop:
        print("fun1")
        time.sleep(1)
        
def fun2(x, y):
    while True:
        print("fun2", x, y)
        time.sleep(1)
        
class Task():
    def __init__(self):
        self.stop = False
    
    def fun1(self):
        while True and not self.stop:
            print("task.fun1")
            time.sleep(1)
        
if __name__ == "__main__":
    task = Task()
    t1 = th.Thread(target=task.fun1)
    t2 = th.Thread(target=lambda: fun2(100, 200))
    t3 = th.Thread(target=fun2, args=('a','b'))
    t1.start()
    task.stop = True
    t2.start()
    t3.start()

    