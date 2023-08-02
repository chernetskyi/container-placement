def clean_double_dict(d):
    # remove empty values from inner dictionary
    res = {x: {y: d[x][y] for y in d[x] if d[x][y]} for x in d}
    # remove empty inner dictionaries
    res = {x: res[x] for x in res if res[x]}
    return res


def get_microservice(micros, container):
    for m in range(len(micros)):
        micro_containers = micros[m].containers
        if container < micro_containers:
            return m
        container -= micro_containers
    raise IndexError('Specified container does not belong to any microservice')


def to_cpu(value):
    cpu = value / 1000
    return round(cpu, 2) if cpu % 1 else int(cpu)
