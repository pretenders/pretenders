from http.server import HTTPServer, BaseHTTPRequestHandler


next_response = 'Response'.encode('utf-8')


class ReplayRequestHandler(BaseHTTPRequestHandler):

    def __getattr__(self, attr):
        if attr.startswith('do_'):
            print("Getting attr {0}".format(attr))
            return self.dispatch
        else:
            raise AttributeError("'{}' not found".format(attr))

    def dispatch(self):
        global next_response
        data = None
        print("{0} {1}".format(self.command, self.path))
        print("Headers:\n{0}".format(self.headers))
        length = int(self.headers.get('Content-Length', 0))
        if length:
            data = self.rfile.read(length)
            print("Data:\n{0}".format(data))
            if self.command == 'RECORD':
                next_response = data
        self.send_response(200)
        self.send_header('Content-Length', len(next_response))
        self.end_headers()
        self.wfile.write(next_response)

    #do_GET = dispatch
    #do_POST = dispatch
    #do_HEAD = dispatch
    #do_OPTIONS = dispatch


if __name__ == '__main__':
        server_address = ('', 8000)
        httpd = HTTPServer(server_address, ReplayRequestHandler)
        httpd.serve_forever()
