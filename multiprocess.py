from multiprocessing import Process
import time

def f(name, name2):
    print('hello', name, name2)
    if name=='alice':
        time.sleep(2.4)

if __name__ == '__main__':
    processes=[None,None]
    processes[0] = Process(target=f, args=('bob', 'cindy',))
    processes[1] = Process(target=f, args=('alice','jim',))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print("all finished")
