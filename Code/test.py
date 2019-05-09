import os
import time
import traceback
from multiprocessing import Pool, Queue
import multiprocessing
import random
 
def handle_error(e):
    '''處理 child process 的錯誤，不然 code 寫錯時，不會回報任何錯誤'''
    traceback.print_exception(type(e), e, e.__traceback__)
    
    
def long_time_task(name):
    print('任務 {} ({}) 開始'.format(name, os.getpid()))
    start = time.time()
    time.sleep(3)
    end = time.time()
    print('任務 {} 執行 {:0.2f} seconds.'.format(name, (end - start)))
 
 
def test(q, num):
    t = random.randint(2,5)
    time.sleep(t)
    q.put(num)
    # return 100

if __name__=='__main__':

    q= multiprocessing.Manager().Queue()
    multiprocessing.freeze_support()
    with Pool(processes=3) as p:
        i = 0
        while True:
            i%=10
            print("new")
            p.apply_async(test, args=(q,i,), error_callback=handle_error)
            i+=1
            if(not q.empty()):
                print(q.get())
            time.sleep(2)
            
            
        p.terminate()
        p.join()