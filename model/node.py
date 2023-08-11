from model.utils import to_cpu


class Node:
    def __init__(self, name, cost, cpulim, memlim, contlim, zone):
        self.name = name
        self.cost = cost
        self.cpu, self.cpulim = 0, cpulim
        self.mem, self.memlim = 0, memlim
        self.cont, self.contlim = 0, contlim
        self.zone = zone

    def info(self):
        def percentage(x, y):
            return f'{round(x / y * 100, 2)}%'

        cpu = f'{to_cpu(self.cpu)}/{to_cpu(self.cpulim)} ({percentage(self.cpu, self.cpulim)}) CPU'
        mem = f'{self.mem}/{self.memlim} ({percentage(self.mem, self.memlim)}) MiB RAM'
        cont = f'{self.cont}/{self.contlim} ({percentage(self.cont, self.contlim)}) containers'

        return f'{cpu}, {mem}, {cont}'

    def __str__(self):
        return f'Node "{self.name}" in zone "{self.zone}": ${self.cost}, {self.info()}'

    def fits(self, container):
        return (self.cpu + container.cpureq) <= self.cpulim and \
               (self.mem + container.memreq) <= self.memlim and \
               (self.cont + 1) <= self.contlim

    def add(self, container, num):
        self.cpu += container.cpureq * num
        self.mem += container.memreq * num
        self.cont += num
