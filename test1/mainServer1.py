# coding: utf-8
import os,sys,socket,six,datetime

from tornado.process import cpu_count,errno_from_exception, errno, _reseed_random
from tornado.log import gen_log
from tornado import web,netutil
from tornado import ioloop
from six.moves import builtins,reload_module
from simpleweb import finup_handler


DEBUG = 0
# 字符串缓存，C语言的对应版本：cstringIO
DEBUG_IO = six.StringIO()
CPU_COUNT = cpu_count()
# 得到当前路径，解决兼容性
THIS_DIRNAME = os.path.abspath(os.getcwd())
EXIT_PENDING = False
listen_port = None
# 创建进程
PORTS = []
ADDR = None
PORT = None
SERVICE_STR = 'maybe this something happen'
def fork_processes(ports=None, max_restarts=100):
    global listen_port
    assert listen_port is None
    assert isinstance(ports, (list, tuple)) and len(ports) > 0, '端口列表不正确.'
    # gen_log.info("Starting service on ports: %s", ports)
    children = {}

    def start_child(port):
# os.fork返回0，则当前是子进程，返回大于0，则是父进程，返回-1，当前进程创建失败，不适用与windows
        pid = os.fork()
        if pid == 0:
            # child process
            _reseed_random()
            # 进程之间资源不共享
            global listen_port
            listen_port = port
            print('FORKED: %s' % port)
            return port
        else:
            children[pid] = port
            return None
# 对传入的端口列表端口遍历得到对每个端口的监听
    for port in ports:
        l_port = start_child(port)
        if l_port is not None:
            return l_port

    num_restarts = 0
    exit_pending = 0
    while True:
        try:
# os.wait()代表等待子进程执行结束,父进程阻塞，两个值分别代表已完成pid，和子进程退出状态，如果没有子进程会引发OSError;
            pid, status = os.wait()
        except KeyboardInterrupt:
            print('Ctrl+C, Exit.')
            sys.exit(0)
        except OSError as e:
            if errno_from_exception(e) == errno.EINTR:
                continue
            if errno_from_exception(e) == errno.ECHILD:
                break
            raise

        if pid not in children:
            continue

        port = children.pop(pid)

        if exit_pending:
            continue
        # 异常结束的子进程
        if os.WIFSIGNALED(status):
            gen_log.warning("child [port:%s] [pid:%d] killed by [signal:%d], restarting", port, pid, os.WTERMSIG(status))
        # 提出子进程的返回值，排除由ctrl+c结束的进程
        elif os.WEXITSTATUS(status) != 0:
            gen_log.warning("child [port:%s] [pid:%d] exited with status %d, restarting", port, pid, os.WEXITSTATUS(status))
        else:
            gen_log.info(   "child [port:%s] [pid:%d] exited normally", port, pid)
            continue
        # 重启次数？
        num_restarts += 1
        if num_restarts > max_restarts:
            raise RuntimeError("child [port:%s] too many restarts, giving up", port)
        l_port = start_child(port)
        if l_port is not None:

            return l_port
    print('Children: %s' % sorted(children.items(), key=lambda x:x[1]))
    print('Main Process Exiting...')
    sys.exit(0)

class MainApplication(web.Application):
    @classmethod
    def ready(MainApp, port, addr=None, family=None, backlog=1048576, reuse_port=True, debug=False, mmfile=None, **kwargs):
        #import pymysql
        #pymysql.install_as_MySQLdb()
        global DEBUG

        import sys
        sys.argv.extend(['--%s=%s' % (k, v) for k, v in {
            'logging': 'debug' if DEBUG else 'error',
            'log_rotate_mode': 'time',
            'log_file_prefix': 'logs/server.%s.log' % port,
            'log_file_num_backups': 30,
            'log_rotate_interval': 1,
            'log_file_max_size': 100 * 1000 * 1000,
            'log_to_stderr': False
        }.items()])

        from tornado import options, locale, log
#        options.parse_config_file("server.conf")
    # 定义服务器监听端口选项
        options.define("port", default=PORT, help="port to listen on")
        # remain_args = options.parse_command_line()
        locale.get()

        settings = {
            'gzip': True,
            'static_url_prefix': "/yihao01-face-recognize/static/",
            'template_path': os.path.join((os.path.dirname(__file__)),'template'),
            'static_path': os.path.join((os.path.dirname(__file__)),'static'),
            'websocket_ping_interval':1,
            'websocket_ping_timeout':5,
            'max_message_size': 16 * 1024 * 1024,
            'cookie_secret': 'abaelhe.0easy.com',
            'cookie_domain': '.0easy.com',
            'token':True,
            'debug': debug,
            'autoreload': debug,
        }

        log.app_log.info( 'Listen:%s:%s\nConfigs:\n%s\nRunning.\n' % (addr, PORTS,
            ''.join(['  %s = %s\n' % (k, v) for k, v in reversed(sorted(options.options.items(), key=lambda i: i[0]))  if k != 'help'])))

        web_handlers = [
            (r'/finup', finup_handler.handler),
            # (r'/sys', handlers.SysHandler),

            #            (r'/sock', handlers.SockHandler),
            #    (r'/yihao01-face-recognize/target', receiver.TargetHandler),
        ]
        sock_handlers = []
        app = MainApp(handlers=web_handlers + sock_handlers, **settings)
        port = int(port)
        app.listen(port, addr=ADDR, debug=debug, reuse_port=reuse_port, **kwargs)


    def listen(self, port, addr=None, family=None, debug=False, reuse_port=True, **kwargs):
        from tornado import httpserver, log, ioloop
        import struct

        flags = 0
        # 判断是否包含对应属性，减少用户程序hold的连接数，减少epoll_ctl和epoll_wait的次数，提高性能，为何使用位--------
        if hasattr(socket, 'TCP_DEFER_ACCEPT'):
            flags |= socket.TCP_DEFER_ACCEPT
        # 发送ack和request，接受ack和reponse一起发送
        if hasattr(socket, 'TCP_QUICKACK'):
            flags |= socket.TCP_QUICKACK
        # ----------
        sockets = netutil.bind_sockets(port, address=addr, backlog=1048576, reuse_port=reuse_port, flags=None if flags == 0 else flags)
        for sock in sockets:
            if not sock.family == socket.AF_INET:
                continue
            #if hasattr(socket, 'SO_LINGER'):
            #    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 0,0))
            #sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack('i', 0))
            #sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, struct.pack('i', 0))
            for i in range(16,0,-1):
                try:
               
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, struct.pack('i', i * 1024 * 1024))
                    print('server sock.SO_RCVBUF: %dM' %(i))
                    print(sock)
                    break
                except:
                    continue
            for i in range(16,0,-1):
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, struct.pack('i', i * 1024 * 1024))
                    print('server sock.SO_SNDBUF: %dM' %(i))
                    break
                except:
                    continue
        # tornado.process.fork_processes(2)
        self.server = httpserver.HTTPServer(self, no_keep_alive=False, **kwargs)
        self.server.add_sockets(sockets)
        self.server.start(1)

        try:
            ioloop.IOLoop.current().start()
        except (KeyboardInterrupt, SystemExit):
            log.app_log.info("\nSystem Exit.\n")
            sys.exit(0)
        except:
            log.app_log.error("System Exception:\n", exc_info=True)
            sys.exit(-1)
        finally:
            self.on_close()

    # def on_close(self):
    #     pass


def model_initializer(procs=None, port=None, addr=None, reuse_port=True):

    global DEBUG,PORT,PORTS,ADDR
    global CPU_COUNT
    global THIS_DIRNAME
    global listen_port
    port = 8888
    argv = []
    reloader = False
    # import finup_model
    # 获取命令行参数，进入选择模式
    for i in sys.argv:
        if i.startswith('--reload'):
            reloader = True
            continue
        if i.startswith('--debug'):
            DEBUG = True
            continue
        if i.startswith('--port'):
            port = int(i.partition('=')[-1])
            continue

    process_num = 1 if DEBUG else (CPU_COUNT if procs is None else procs)
    ports = [(int(port) + i) for i in range(process_num)]
    port = fork_processes(ports)
    iol = ioloop.IOLoop.current()
    finup_handler.LoadModel().load_model()
    import socket
    reload_module(socket)
    from tornado import options, locale, log
    reload_module(options)
    reload_module(log)
    # from handlers import finup_handler
    # reload_module(finup_handler)

    # import finup_model
    # reload_module(finup_model)
    # 判断地址是否为空，地址何处获得
    if addr is not None:
        ADDR = addr
    PORT = port
    # 将finup_model中没有的端口，添加进入原列表中
    PORTS.extend([i for i in ports if i not in PORTS])
    dumpfile = os.sep.join([THIS_DIRNAME, 'logs', 'support%s.dat' % ('' if DEBUG else ('.%s' % listen_port))])
    max_buffer = 4096 * 1024 * 1024
    max_chunk = 128 * 1024 * 1024
    try:
        MainApplication.ready(port, addr=ADDR, debug=DEBUG,
                              reuse_port=reuse_port,
                              max_body_size=max_buffer,
                              max_buffer_size=max_buffer,
                              chunk_size=max_chunk,
                              decompress_request=True,
                              idle_connection_timeout=5000, body_timeout=1200000)
        ## decompress_request=True, 自动解压GZIP: curl -s -F 'files=@./fanpu_20180403_v2.txt;type=csv/gzip' 'http://127.0.0.1:8889/finup?model=1&stats=1' > ./data.8889.txt  &
    except KeyboardInterrupt:
        print("W: interrupt received, stopping…")
    except:
        try:
            with open(dumpfile, 'wb') as support_file:
                support_file.write('>>>> %s\n' % datetime.datetime.now().isoformat())
                support_file.write(SERVICE_STR % dumpfile)
                support_file.flush()
        except:
            pass

if __name__  == '__main__':
    model_initializer()
