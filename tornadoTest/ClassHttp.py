from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import time,threading

starttime = time.time()

class RequestHandler(BaseHTTPRequestHandler):
    def _writeheaders(self,doc):
        if doc is None:
            self.send_response(404)
        else:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()

    def _getdoc(self,filename):
        if filename == '/f':
            return 'something filename start file'
        elif filename == '/s':
            return 'give stats data'
        else:
            return None

    def do_HEAD(self):
        doc = self._getdoc(self.path)
        self._writeheaders(doc)

    def do_GET(self):
        doc = self._getdoc(self.path)
        self._writeheaders(doc)
        if doc is None:
            self.wfile.write('aaa')
        else:
            self.wfile.write(doc)

class ThreadingHTTPServer(ThreadingMixIn,HTTPServer):
    pass



if __name__ == '__main__':
    serveraddr = ('',8765)
    srvr = ThreadingHTTPServer(serveraddr,RequestHandler)
    srvr.serve_forever()