import socket
import docker

try:
    from checks import AgentCheck
except ImportError:
    from datadog_checks.checks import AgentCheck


class DockerSwarm(AgentCheck):

    def check(self, instance):

        metric = "docker_swarm.running"
        host_name = socket.gethostbyname(socket.gethostname())
        tag = 'host:%s' % host_name

        client = docker.from_env()

        try:
            manager_nodes = client.nodes(filters={'role': 'manager'})

            if manager_nodes:
                self.gauge(metric, 1, tags=[tag])
            else:
                self.gauge(metric, 0, tags=[tag])
        except Exception:
            self.gauge(metric, 0, tags=[tag])