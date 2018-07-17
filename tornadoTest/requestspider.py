import urllib2
import threadpool
import time
from time import sleep

def requesturl(aa):
    time1 = time.time()
    url = 'http://127.0.0.1:8380'
    req = urllib2.urlopen(urllib2.Request(url))
    # test = req.readlines()
    time2 = time.time()
    print('cutime:%s'% (time2-time1))

# requesturl()
# while True:
#     url = 'http://127.0.0.1:8380'
#     req= urllib2.urlopen(urllib2.Request(url))
#     test = req.readlines()
#     print(test)
pool = threadpool.ThreadPool(1000)
aa = [a for a in range(1000)]
requests = threadpool.makeRequests(requesturl,aa)
[pool.putRequest(req) for req in requests]
pool.wait()
