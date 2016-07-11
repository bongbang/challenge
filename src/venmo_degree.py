from __future__ import division, print_function
import json
from datetime import strptime

nodes = {}

with open('../_myfiles/first_test.txt') as f:
# with open('../data-gen/v20.txt') as f:
    transaction = json.loads(f.readline())

try:
    transact_time = strptime(transaction['created_time'], '%Y-%m-%dT
# "2016-04-07T03:35:02Z"}

for x in ['actor', 'target']:
    node = transaction[x]
    nodes[node] = nodes.get(node, 0) + 1

print(nodes)
