# the following try/except block will make the custom check compatible with any Agent version
try:
    # first, try to import the base class from old versions of the Agent...
    from checks import AgentCheck
except ImportError:
    # ...if the above failed, the check is running in Agent version 6 or later
    from datadog_checks.checks import AgentCheck

# content of the special variable __version__ will be shown in the Agent status page
__version__ = "1.0.0"

import socket

class MCRouterCheck(AgentCheck):
  def check(self, instance):
    connection = socket.create_connection(('127.0.0.1', 11211))
    connection.sendall("stats all\r\n")
    connection.shutdown(socket.SHUT_WR)
    result = ''
    while 1:
      data = connection.recv(1024)
      if data == "":
        break
      result += data
    for line in result.split("\n"):
      line = line.strip()
      if not line.startswith("STAT "):
        continue
      stat = line.split(' ')
      # See https://github.com/facebook/mcrouter/wiki/Stats-commands - some stats
      # are not counters - e.g. configuration or the version
      if len(stat) == 3:
        self.gauge('mcrouter.'+stat[1], stat[2], tags=['mcrouter'])
    connection = socket.create_connection(('127.0.0.1', 11211))
    connection.sendall("stats servers\r\n")
    connection.shutdown(socket.SHUT_WR)
    result = ''
    while 1:
      data = connection.recv(1024)
      if data == "":
        break
      result += data
    for line in result.split("\n"):
      line = line.strip()
      if not line.startswith("STAT "):
        continue
      stats = line.split(' ')
      # example line: STAT mem001-dsdev-uswest2:11211:ascii:plain:notcompressed-1000 avg_latency_us:699.046 pending_reqs:0 inflight_reqs:0 avg_retrans_ratio:0 max_retrans_ratio:0 min_retrans_ratio:0 closed:1; deleted:161138 found:7603202 notfound:14183173 stored:1925288
      # WTF???? why does closed have a semicolon????
      for stat in stats[2:]:
        if stat[-1] == ';':
          stat = stat[:-1]
        stat = stat.split(':')
        self.gauge('mcrouter.'+stat[0], stat[1], tags=['mcrouter', 'server:'+stats[1].replace(':','_')])
