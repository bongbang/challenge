# from __future__ import division, print_function
# no need since using Python 3
import json
from datetime import datetime, timedelta
from collections import deque, defaultdict
from bisect import insort

class Transaction_graph:
    def __init__(self):
        self.log = defaultdict(set)
        self.time_log = deque()
        self.nodes_tally = defaultdict(lambda: 0)
        self.degree_bins = [0]*16 # pre-allocate TODO more?
        self.median_degree = 0

    def add_to_logs(self,node_set,time):
        if time not in self.log:
            insort(self.time_log, time)
        self.log[time] |= {node_set}

    def add_transaction(self,actor,target,time):
        try:
            time_diff = time - self.time_log[-1]
        except IndexError: # first time only
            node_set = tuple(sorted([actor,target]))
            self.add_to_logs(node_set,time)
            for node in node_set:
                self.nodes_tally[node] += 1
            self.degree_bins[1] = 2
            self.median_degree = 1
        else:
            print(actor, target, time_diff)



## MAIN
venmo = Transaction_graph()
with open('../venmo_input/first_test.txt') as f:
    for line in f:
        txn = json.loads(line)  # transaction
        try:
            time = datetime.strptime(txn['created_time'], '%Y-%m-%dT%H:%M:%SZ') # TODO test error
        except:
            continue
        else:
            actor = txn['actor']
            target = txn['target']
            try:
                if not actor or not target or actor == target:
                    raise NameError('Invalid actor or target.')
            except:
                continue
            else:
                venmo.add_transaction(actor,target,time)
