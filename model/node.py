class Node:
    def __init__(self, name, cost, cpulim, memlim, contlim, zone):
        self.name = name
        self.cost = cost
        self.cpulim = cpulim
        self.memlim = memlim
        self.contlim = contlim
        self.zone = zone
        self.cpu = 0
        self.mem = 0
        self.cont = 0

    def __str__(self):
        return f'Node "{self.name}" in zone "{self.zone}": ${self.cost}, {self.cpulim} mCPU, {self.memlim} MiB RAM, up to {self.contlim} containers'

    def fits(self, container):
        return (self.cpu + container.cpureq) <= self.cpulim and \
               (self.mem + container.memreq) <= self.memlim and \
               (self.cont + 1) <= self.contlim
