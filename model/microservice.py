class Microservice:
    def __init__(self, name, cpureq, memreq, num_containers):
        self.name = name
        self.cpureq = cpureq
        self.memreq = memreq
        self.num_containers = num_containers

    def __str__(self):
        return f'Microservice "{self.name}" ({self.num_containers} containers): {self.cpureq} vCPU, {self.memreq} MiB RAM'
