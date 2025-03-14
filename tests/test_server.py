import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer


class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        file_path = None

        if self.path == '/empty_json/mentors':
            file_path = 'tests/test_data/empty_json/mentors.json'
        elif self.path == '/empty_json/postcards':
            file_path = 'tests/test_data/empty_json/postcards.json'

        elif self.path == '/invalid_json/mentors':
            file_path = 'tests/test_data/invalid_json/mentors.json'
        elif self.path == '/invalid_json/postcards':
            file_path = 'tests/test_data/invalid_json/postcards.json'

        elif self.path == '/3_mentors_5_postcards/mentors':
            file_path = 'tests/test_data/3_mentors_5_postcards/mentors.json'
        elif self.path == '/3_mentors_5_postcards/postcards':
            file_path = 'tests/test_data/3_mentors_5_postcards/postcards.json'

        elif self.path == '/extra_collection/mentors':
            file_path = 'tests/test_data/extra_collection/mentors.json'
        elif self.path == '/extra_collection/postcards':
            file_path = 'tests/test_data/extra_collection/postcards.json'

        elif self.path == '/extra_fields/mentors':
            file_path = 'tests/test_data/extra_fields/mentors.json'
        elif self.path == '/extra_fields/postcards':
            file_path = 'tests/test_data/extra_fields/postcards.json'

        elif self.path == '/i_am_mentor/mentors':
            file_path = 'tests/test_data/i_am_mentor/mentors.json'
        elif self.path == '/i_am_mentor/postcards':
            file_path = 'tests/test_data/i_am_mentor/postcards.json'

        elif self.path == '/long_name_postcard/mentors':
            file_path = 'tests/test_data/long_name_postcard/mentors.json'
        elif self.path == '/long_name_postcard/postcards':
            file_path = 'tests/test_data/long_name_postcard/postcards.json'

        elif self.path == '/many_mentors_postcards/mentors':
            file_path = 'tests/test_data/many_mentors_postcards/mentors.json'
        elif self.path == '/many_mentors_postcards/postcards':
            file_path = 'tests/test_data/many_mentors_postcards/postcards.json'

        elif self.path == '/missing_fields/mentors':
            file_path = 'tests/test_data/missing_fields/mentors.json'
        elif self.path == '/missing_fields/postcards':
            file_path = 'tests/test_data/missing_fields/postcards.json'

        elif self.path == '/template_name/mentors':
            file_path = 'tests/test_data/template_name/mentors.json'
        elif self.path == '/template_name/postcards':
            file_path = 'tests/test_data/template_name/postcards.json'

        elif self.path == '/wrong_types/mentors':
            file_path = 'tests/test_data/wrong_types/mentors.json'
        elif self.path == '/wrong_types/postcards':
            file_path = 'tests/test_data/wrong_types/postcards.json'

        elif self.path == '/file_not_found/mentors':
            file_path = 'tests/test_data/file_not_found/mentors.json'
        elif self.path == '/file_not_found/postcards':
            file_path = 'tests/test_data/file_not_found/postcards.json'

        elif self.path == '/internal_server_error/mentors':
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Internal Server Error"}')
            return

        elif self.path == '/bad_request/mentors':
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Bad Request"}')
            return
        
        if not file_path:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')
            return

        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
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