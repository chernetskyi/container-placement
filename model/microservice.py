class Microservice:
    def __init__(self, name, cpureq, memreq, containers):
        self.name = name
        self.cpureq = cpureq
        self.memreq = memreq
        self.containers = containers

    def __str__(self):
        return f'Microservice "{self.name}" ({self.containers} containers): {self.cpureq} mCPU, {self.memreq} MiB RAM'
