import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer


class TestServerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Requested path: {self.path}")
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            welcome_message = """
                <html>
                    <meta charset="UTF-8">
                    <head><title>Тестовый сервер</title></head>
                    <body>
                        <h1>Добро пожаловать на тестовый сервер!</h1>
                        <p>Доступные эндпоинты:</p>
                        <ul>
                            <li><a href="/empty_json/mentors">/empty_json/mentors</a></li>
                            <li><a href="/empty_json/postcards">/empty_json/postcards</a></li>
                            <li><a href="/invalid_json/mentors">/invalid_json/mentors</a></li>
                            <li><a href="/invalid_json/postcards">/invalid_json/postcards</a></li>
                            <li><a href="/3_mentors_5_postcards/mentors">/3_mentors_5_postcards/mentors</a></li>
                            <li><a href="/3_mentors_5_postcards/postcards">/3_mentors_5_postcards/postcards</a></li>
                            <li><a href="/extra_collection/mentors">/extra_collection/mentors</a></li>
                            <li><a href="/extra_collection/postcards">/extra_collection/postcards</a></li>
                            <li><a href="/extra_fields/mentors">/extra_fields/mentors</a></li>
                            <li><a href="/extra_fields/postcards">/extra_fields/postcards</a></li>
                            <li><a href="/i_am_mentor/mentors">/i_am_mentor/mentors</a></li>
                            <li><a href="/i_am_mentor/postcards">/i_am_mentor/postcards</a></li>
                            <li><a href="/long_name_postcard/mentors">/long_name_postcard/mentors</a></li>
                            <li><a href="/long_name_postcard/postcards">/long_name_postcard/postcards</a></li>
                            <li><a href="/many_mentors_postcards/mentors">/many_mentors_postcards/mentors</a></li>
                            <li><a href="/many_mentors_postcards/postcards">/many_mentors_postcards/postcards</a></li>
                            <li><a href="/missing_fields/mentors">/missing_fields/mentors</a></li>
                            <li><a href="/missing_fields/postcards">/missing_fields/postcards</a></li>
                            <li><a href="/template_name/mentors">/template_name/mentors</a></li>
                            <li><a href="/template_name/postcards">/template_name/postcards</a></li>
                            <li><a href="/wrong_types/mentors">/wrong_types/mentors</a></li>
                            <li><a href="/wrong_types/postcards">/wrong_types/postcards</a></li>
                            <li><a href="/file_not_found/mentors">/file_not_found/mentors</a></li>
                            <li><a href="/file_not_found/postcards">/file_not_found/postcards</a></li>
                            <li><a href="/internal_server_error/mentors">/internal_server_error/mentors</a></li>
                            <li><a href="/bad_request/mentors">/bad_request/mentors</a></li>
                        </ul>
                    </body>
                </html>
                """
            self.wfile.write(welcome_message.encode('utf-8'))
            return

        file_path = None

        path_mapping = {
            '/empty_json/mentors': 'tests/test_data/empty_json/mentors.json',
            '/empty_json/postcards': 'tests/test_data/empty_json/postcards.json',
            '/invalid_json/mentors': 'tests/test_data/invalid_json/mentors.json',
            '/invalid_json/postcards': 'tests/test_data/invalid_json/postcards.json',
            '/3_mentors_5_postcards/mentors': 'tests/test_data/3_mentors_5_postcards/mentors.json',
            '/3_mentors_5_postcards/postcards': 'tests/test_data/3_mentors_5_postcards/postcards.json',
            '/extra_collection/mentors': 'tests/test_data/extra_collection/mentors.json',
            '/extra_collection/postcards': 'tests/test_data/extra_collection/postcards.json',
            '/extra_fields/mentors': 'tests/test_data/extra_fields/mentors.json',
            '/extra_fields/postcards': 'tests/test_data/extra_fields/postcards.json',
            '/i_am_mentor/mentors': 'tests/test_data/i_am_mentor/mentors.json',
            '/i_am_mentor/postcards': 'tests/test_data/i_am_mentor/postcards.json',
            '/long_name_postcard/mentors': 'tests/test_data/long_name_postcard/mentors.json',
            '/long_name_postcard/postcards': 'tests/test_data/long_name_postcard/postcards.json',
            '/many_mentors_postcards/mentors': 'tests/test_data/many_mentors_postcards/mentors.json',
            '/many_mentors_postcards/postcards': 'tests/test_data/many_mentors_postcards/postcards.json',
            '/missing_fields/mentors': 'tests/test_data/missing_fields/mentors.json',
            '/missing_fields/postcards': 'tests/test_data/missing_fields/postcards.json',
            '/template_name/mentors': 'tests/test_data/template_name/mentors.json',
            '/template_name/postcards': 'tests/test_data/template_name/postcards.json',
            '/wrong_types/mentors': 'tests/test_data/wrong_types/mentors.json',
            '/wrong_types/postcards': 'tests/test_data/wrong_types/postcards.json',
            '/file_not_found/mentors': 'tests/test_data/file_not_found/mentors.json',
            '/file_not_found/postcards': 'tests/test_data/file_not_found/postcards.json'
        }

        file_path = path_mapping.get(self.path)

        if self.path == '/internal_server_error/mentors':
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

        with open(file_path, 'r', encoding='utf-8') as file_:
            data = json.load(file_)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=TestServerHandler, port=8000):
    server_address = ('127.0.0.1', port)
    http_server = server_class(server_address, handler_class)
    print(f'Сервер для тестов успешно запущен: http://{server_address[0]}:{port}')
    http_server.serve_forever()


if __name__ == "__main__":
    run()