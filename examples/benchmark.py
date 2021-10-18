import time
from multiprocessing import Process

from grpc_client import run

if __name__ == '__main__':
    t1 = time.time()
    processes = []
    execute_count = 1000
    for i in range(execute_count):
        p = Process(target=run)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    t2 = time.time()
    print('Execution took %s seconds' % (t2 - t1))
