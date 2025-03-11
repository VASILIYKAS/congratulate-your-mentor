from http.server import SimpleHTTPRequestHandler, HTTPServer
import json


class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path == '/empty':
            file_path = 'tests/test_data/empty.json'

        elif self.path == '/invalid':
            file_path = 'tests/test_data/invalid_json.json'

        elif self.path == '/missing_fields':
            file_path = 'tests/test_data/missing_fields.json'

        elif self.path == '/wrong_types':
            file_path = 'tests/test_data/wrong_types.json'

        elif self.path == '/extra_data':
            file_path = 'tests/test_data/mentors_data_extra.json'

        elif self.path == '/internal_server_error':
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Internal Server Error"}')
            return

        elif self.path == '/bad_request':
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Bad Request"}')
            return

        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "File not found"}')
            return

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        with open(file_path, 'r', encoding='utf-8') as file_:
            data = json.load(file_)
            self.wfile.write(json.dumps(data).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f'Сервер для тестов успешно запущен: http://{server_address[0]}:{port}')
    httpd.serve_forever()


if __name__ == "__main__":
    run()