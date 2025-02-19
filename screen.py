import time
import socketserver
import http.server
import mss
import io
import os
from PIL import Image
from urllib.parse import parse_qs

os.system('xhost +')
os.system('export DISPLAY=:0')

URL_USERNAME = "7ebd5d66f19edb93fd474a7272a27f4956035afbc152e463"
URL_PASSWORD = "b49165cef79dcdb3a9ab89544fb668b8aca19ccfe6256ac5"
ADV_USERNAME = "jakub515.szczurek@gmail.com"
ADV_PASSWORD = "123"

LOGIN_HTML = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logowanie</title>
</head>
<body>
    <h2>Logowanie</h2>
    <form action="/auth" method="post">
        <label for="username">Nazwa użytkownika:</label>
        <input type="text" id="username" name="username" required>
        <br>
        <label for="password">Hasło:</label>
        <input type="password" id="password" name="password" required>
        <br>
        <button type="submit">Zaloguj</button>
    </form>
</body>
</html>
"""

class VideoStreamHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/auth/":
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode('utf-8'))

        elif self.path == "/auth/"+URL_USERNAME+"/"+URL_PASSWORD:
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            self.stream()
        else:
            pass

    def do_POST(self):
        if self.path == "/auth":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            fields = parse_qs(post_data)
            username = fields.get("username", [""])[0]
            password = fields.get("password", [""])[0]
            if username == ADV_USERNAME and password == ADV_PASSWORD:
                self.send_response(200)
                self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
                self.end_headers()
                self.stream()
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(LOGIN_HTML.encode('utf-8'))

    def stream(self):
        with mss.mss() as sct:
            while True:
                screenshot = sct.grab(sct.monitors[1])  # Pobiera cały ekran

                # Konwersja do JPEG zamiast PNG (dużo szybsze)
                img_byte_arr = io.BytesIO()
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                # Zmniejszamy rozdzielczość dla wydajności (np. 50% oryginału)
                img = img.resize((screenshot.width // 2, screenshot.height // 2))

                # Zapis do JPEG z kompresją
                img.save(img_byte_arr, format='JPEG', quality=50)
                img_byte_arr.seek(0)

                # Wysyłanie klatek
                self.wfile.write(b'--frame\r\n')
                self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                self.wfile.write(img_byte_arr.read())
                self.wfile.write(b'\r\n')

                time.sleep(0.03)  # 30 FPS

class VideoStreamServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

def run(port=8000):
    server_address = ('', port)
    httpd = VideoStreamServer(server_address, VideoStreamHTTPRequestHandler)
    print(f"Serwer działa na porcie {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

