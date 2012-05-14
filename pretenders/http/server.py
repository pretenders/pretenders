from http.server import HTTPServer, BaseHTTPRequestHandler


next_responses = []


class ReplayRequestHandler(BaseHTTPRequestHandler):

    def __getattr__(self, attr):
        if attr.startswith("do_"):
            print("Getting attr {0}".format(attr))
            return self.dispatch
        else:
            raise AttributeError("'{}' not found".format(attr))

    def dispatch(self):
        data = None
        print("{0} {1}".format(self.command, self.path))
        print("Headers:\n{0}".format(self.headers))
        length = int(self.headers.get("Content-Length", 0))
        if length:
            data = self.rfile.read(length)
            print("Data:\n{0}".format(data))
        if self.command == "RECORD":
            next_responses.append(data)
            self.respond(200, b"OK")
        elif len(next_responses):
            body = next_responses.pop(0)
            self.respond(200, body)
        else:
            self.respond(404, b"No preset response")

    def respond(self, status, body):
        self.send_response(status)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


def run_raw(port=8000):
    server_address = ("localhost", port)
    httpd = HTTPServer(server_address, ReplayRequestHandler)
    httpd.serve_forever()


from bottle import request, response, route, run, get, post


def respond(status, body):
    response.status = status
    return body


@route('/mock', method='ANY')
def replay():
    if len(next_responses):
        body = next_responses.pop(0)
        return respond(200, body)
    else:
        return respond(404, b"No preset response")


@post('/preset')
def add_preset():
    next_responses.append(request.body)
    return respond(200, b"OK")


def run_bottle(port=8000):
    run(host='localhost', port=port)


if __name__ == "__main__":
    run_bottle()
