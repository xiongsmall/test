# coding: utf-8

str = '''
POST /Finup HTTP/1.0
Content-length: 247
Content-type: application/post
Host: 127.0.0.1:9999
User-Agent: ApacheBench/2.3
Accept: */*

asndankdnakdnajknsnajnjanjasjdajdakqdkjsandjansd baaskjdbsadkjanlsdajsdjkansjdansdankdnalsdnjkas
cansjxncdsmcdklalmndsnaldkjsakjldnnkadnjasnjdnadsnanjldsalsdmasm,d mamsdmamsdmas,mda.,dm.am,sdma
dam,dm,sanmdmamsdmnas,m.dmasmdmasmdmsadas,dsada.s,da
'''
import re
data1 = re.search(r'\n\n([\s\S]*)', str).group(1)
print('data1:',data1)


data2 = re.search(r'.* (/.*) ',str)
print('data2:',data2.group(1))

items = '''[[0.966780, '0', '1', '6', '湖北省', '武汉', 7.0, 0.0, 0.0, 0, 0, 5],
         [0.966780, '0', '1', '6', '湖北省', '武汉', 7.0, 0.0, 0.0, 0, 0, 5],
         [0.966780, '0', '1', '6', '湖北省', '武汉', 7.0, 0.0, 0.0, 1, 0, 5]]'''
item = list(items)
print(type(item))


import threadpool
def getdata(str):
    datalines = str.splitlines()
    Index = None
    for index, str in enumerate(datalines):
        if not str:
            Index = index
    dataline = datalines[Index + 1:]
    data = ''.join(dataline)
    if type(data) == list:
        return eval(data)
    else:
        return data

def thread_way():
    pool = threadpool.ThreadPool(2)
    somereq = threadpool.makeRequests(getdata,[str])
    for req in somereq:
        pool.putRequest(req)
    aaa = pool.wait()
    print(aaa)

thread_way()

