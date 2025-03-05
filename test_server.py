from http.server import SimpleHTTPRequestHandler, HTTPServer
import json


class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/': 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            welcome_message = """
                <html>
                    <meta charset="UTF-8">
                    <head><title>Тестовый сервер</title></head>
                    <body>
                        <h1>Добро пожаловать на сервер!</h1>
                        <p>Доступные эндпоинты:</p>
                        <ul>
                            <li><a href="/mentors">/mentors</a></li>
                            <li><a href="/congratulations">/congratulations</a></li>
                            <li><a href="/asciiart">/asciiart</a></li>
                        </ul>
                    </body>
                </html>
                """
            self.wfile.write(welcome_message.encode('utf-8'))
            return
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        if self.path == '/mentors':
            file_path = 'data/mentors.json'

        elif self.path == '/congratulations':
            file_path = 'data/congratulations.json'
        
        elif self.path == '/asciiart':
            file_path = 'data/ascii_art.json'
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "File not found"}')
            return

        with open(file_path, 'r', encoding='utf-8') as file_:
            data = json.load(file_)
            self.wfile.write(json.dumps(data).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f'Сервер запущен: http://{server_address[0]}:{port}')
    httpd.serve_forever()


if __name__ == "__main__":
    run()