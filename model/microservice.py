from model.utils import to_cpu


class Microservice:
    def __init__(self, name, cpureq, memreq, containers):
        self.name = name
        self.cpureq = cpureq
        self.memreq = memreq
        self.containers = containers

    def __str__(self):
        return f'Microservice "{self.name}" ({self.containers} containers): {to_cpu(self.cpureq)} CPU, {self.memreq} MiB RAM'
