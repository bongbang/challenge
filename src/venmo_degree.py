#!/usr/bin/env python3
from __future__ import print_function
import json
from datetime import datetime, timedelta
from collections import deque, defaultdict
from bisect import insort
import argparse
import sys

try:
    assert sys.version_info >= (3,5)
except AssertionError:
    print('\n*** Need Python version 3.5 or above! ***\n')
    print('Your version is: {}\n'.format(sys.version))
    sys.exit()

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str)
parser.add_argument('output_file', type=str)

args = parser.parse_args()

class Transaction_graph:
    def __init__(self):
        self.log = defaultdict(set)
        self.time_log = deque()
        self.nodes_tally = defaultdict(lambda: 0)
        self.degree_bins = [0]*32 # pre-allocate
        self.median_degree = 0

    def _make_edge(self,actor,target):
        return tuple(sorted([actor,target]))

    def _add_edge(self,edge,timestamp):
        if timestamp not in self.log:
            try:
                insort(self.time_log, timestamp)
            except AttributeError:
                raise EnvironmentError('Need Python version 3.5 or above.')
        self.log[timestamp].add(edge)

    def _process_first_transaction(self,actor,target,timestamp):
        edge = self._make_edge(actor,target)
        self._add_edge(edge,timestamp)
        for node in edge:
            self.nodes_tally[node] = 1
        self.degree_bins[1] = 2
        self.median_degree = 1

    def _update_degrees(self,edge,up=True):
        bump = 1 if up else -1
        for node in edge:
            if not up and self.nodes_tally[node] == 1:
                self.nodes_tally.pop(node)
                self.degree_bins[1] -= 1
            else:
                degree_old = self.nodes_tally[node]
                self.nodes_tally[node] += bump
                try:
                    self.degree_bins[degree_old + bump] += 1
                except IndexError:
                    self.degree_bins.append(1)
                if degree_old:
                    self.degree_bins[degree_old] -= 1

    def _evict_edges(self):
        cutoff = self.time_log[-1] - timedelta(seconds=60)
        while self.time_log[0] <= cutoff:
            time_evicted = self.time_log.popleft()
            edges_evicted = self.log.pop(time_evicted)
            # import pdb; pdb.set_trace()
            for edge in edges_evicted:
                self._update_degrees(edge,up=False)

    def _find_duplicate(self,edge,timestamp):
        if all(node in self.nodes_tally for node in edge):
            for time, edges in self.log.items():
                if edge in edges:
                    if time < timestamp:
                        edges.remove(edge) # (below) action for cases t_diff <= 0 || t_diff > 0
                        return 1 # found older & removed: set new edge, no update tally || no update tally
                    else:
                        return 2 # found newer/equal: no new edge, no update tally || update (found just added)
            else:
                return False # not found: set new edge, update || update tally
        else:
            return False # not found: ditto

    def _update_median(self):
        position = (len(self.nodes_tally) + 1) * 0.5
        cum_count = 0
        for degree, count in enumerate(self.degree_bins):
            cum_count += count
            delta = cum_count - position
            if delta <= -1:
                continue
            elif delta >= 0:
                self.median_degree = degree
                break
            else: # i.e. falls 0.5 positions short
                for i, next_count in enumerate(self.degree_bins[degree+1:]):
                    if next_count > 0: break
                self.median_degree = degree + (i+1)*0.5
                break

    def add_transaction(self,actor,target,timestamp):
        try:
            time_diff = timestamp - self.time_log[-1]
        except IndexError: # first time only
            self._process_first_transaction(actor,target,timestamp)
        else:
            if time_diff >= timedelta(seconds=60):
                self.__init__() # reset: back to square 1
                self._process_first_transaction(actor,target,timestamp)

            elif time_diff > timedelta():
                edge = self._make_edge(actor,target)
                self._add_edge(edge,timestamp)
                self._evict_edges()
                found = self._find_duplicate(edge,timestamp)
                if not found or found == 2:
                    self._update_degrees(edge) # just update tally since edge already added
                    self._update_median()
                # else: pass # found and killed duplicate, so no change

            elif time_diff > -timedelta(seconds=60):
                edge = self._make_edge(actor,target)
                found = self._find_duplicate(edge,timestamp)
                if not found:
                    self._add_edge(edge,timestamp)
                    self._update_degrees(edge)
                    self._update_median()
                elif found == 1:
                    self._add_edge(edge,timestamp)
                # else: pass # found newer, so no change.

            # else: pass # transaction outside window. Do nothing.

    # print functions for easier debugging
    def stat(self):
        for node, degree in self.nodes_tally.items():
            print('{:20} : {:3d}'.format(node, degree))
        print()
        for degree, count in enumerate(self.degree_bins):
            if count:
                print('{:2d} : {:3d}'.format(degree, count))

    def plog(self):
        for time in self.time_log:
            print('{} : {}'.format(time, self.log[time]))

## MAIN
v = Transaction_graph() # v for Venmo, but abbreviated for quick debugging
with open(args.input_file, 'r') as file_in:
    with open(args.output_file, 'w') as file_out:
        for line in file_in:
            txn = json.loads(line)  # transaction
            try:
                timestamp = datetime.strptime(txn['created_time'], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                continue
            else:
                actor = txn['actor']
                target = txn['target']
                try:
                    if not actor or not target or actor == target:
                        raise NameError('Invalid actor or target.')
                except NameError:
                    continue
                else:
                    v.add_transaction(actor,target,timestamp)
                    assert 0 not in v.nodes_tally.values()
                    file_out.write('{:.2f}\n'.format(v.median_degree))
