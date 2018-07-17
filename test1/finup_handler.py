# coding: utf-8
import queue
from multiprocessing import Pool
import gzip,six,time,json,os,imp,tornadis
import tornado.web
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from celery import Celery
# import tcelery
# celery = Celery('tasks',backend='',broker='')
MODELS = dict()
q = queue.Queue(100)
pool = Pool(5)
class handler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(4)
    # @gen.coroutine
    def get(self):
        self.finish(','.join(MODELS.keys()))
    #
    # @celery.task
    # def funthread(self):
    #     data = self.get_origin()
    #     data = self.format_input(data)
    #     ret = self.process_data(data)
    #     return ret


    @gen.coroutine
    def post(self):
        print('post in ')
        model = self.get_argument('model', None)
        self.format = self.get_argument('format', None)
        if not model:
            self.finish('this is None')
        if model in MODELS.keys():
            self.pro_model = MODELS[model]
        else:
           self.finish('this model display')
        # ret = yield tcelery.celery_task(self.funthread,)
        # print(ret)

        # ----
        # self.get_origin(model)
        # self.format_input()
        # self.process_data()
        # if gen.is_coroutine_function(self.get_origin):
        #     yield gen.Task(self.get_origin)
        # self.data = self.request.body.strip()
        # self.format_input()
        # ----
        # q.put(self.data)
        # while True:
        #     pool.apply_async(self.process_data)
        # ret = yield self.process_data()
        # if gen.is_coroutine_function(self.process_data):
        #     ret = yield gen.Task(self.process_data,)
        # yield thread_pool.submit(self.process_data,)
        # print(ret)
            # raise gen.Return(ret)

        # ------
        # data = yield self.get_origin()
        # data = yield self.format_input(data)
        # ret = yield self.process_data(data)
        # print(ret)





# 执行方法，跑模型
#     @gen.coroutine
    def process_data(self,data):
        import requests
        # from tornado.httpclient import AsyncHTTPClient
        # http_client = AsyncHTTPClient()
        # if gen.is_coroutine_function(requests.get):
        #     print(1111)
        # aaa = yield requests.get('http://www.google.com')
        # bbb =yield http_client.fetch('http://www.google.com')
        # time = int(time)
        # num = 0
        # while num<time:
        #     num = num+1
        #     print(num)
        # yield gen.sleep(time)
        # if q.qsize()>0:
        #     data = q.get()
        t = time.time()
        print(t)
        predict_proba = self.pro_model.predict_proba
        self.ret = predict_proba(data)
        print('Time:%s'%(time.time()-t))
        # ret = predict_proba(self.data)
        # print(ret)

        # if gen.is_coroutine_function(predict_proba):
        #     yield gen.Task(predict_proba(self.data))
        # elif callable(predict_proba):
        #     self.ret = predict_proba(self.data)
        # print(self.ret)
        return(self.ret)

    # 是否上传文件
    # @gen.coroutine
    def get_origin(self):
        self.data = ''
        if len(self.request.files.get('files', [])) > 0:
            self.data = self.request.files["files"][0].pop("body").strip()
            try:
            # 此处加入判断文件类型 -------
                self.data = gzip.GzipFile(fileobj=six.StringIO(self.data), mode='rb').read().strip()
            except:
                pass
        else:
            self.data = self.request.body.strip()
        return self.data




# 传入数据类型判断，并转换或切割
#     @gen.coroutine
    def format_input(self,data):
        fmt = self.format
        if fmt == 'json':
            data = json.loads(data)
        elif fmt == 'csv':
            data =( i.split('|') for i in  data.split(b'\n') if i.strip() )
        return data
        # elif hasattr(self.pro_model, 'format_input'):
        #     self.pro_model.format_input(self, fmt=fmt)




# 连接redis
REDIS = None
def get_redis():
    global REDIS
    if not REDIS:
        REDIS = tornadis.Client(host='10.19.97.227', port='6379', password='aace52100ec293bc6e3220dbda812155')
    return REDIS

# 对存在的模型进行加载
class LoadModel(object):
    def load_model(self):
        models = dict()
        dirpath = os.path.abspath(os.sep.join([os.getcwd(),'models']))
        modeldir =os.listdir(dirpath)
        for mofile in modeldir:
            fname = mofile.split('.')[0]
            moname = mofile.split('_model')[0]
            if mofile.endswith('_model.py'):
                # py3 不推荐imp，寻找替代
                mod = imp.load_source(fname,os.sep.join([dirpath, mofile]))
                models[moname] = mod
        self.update(models)

    def update(self,models):
        global MODELS
        old_model = MODELS
        MODELS = models
        for i in old_model.keys():
            m = old_model.pop[i,None]
            if m:
                del m
        del old_model