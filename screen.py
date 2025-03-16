import sys
import os
import subprocess

#get pid-u
pid = os.getpid()
print("pid: ",pid)
#wgranie konfiguracji
def load_config(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

if getattr(sys, 'frozen', False):  # Jeśli uruchomiono z pliku .exe
    config_path = os.path.join(sys._MEIPASS, '.config')
    image_path = os.path.join(sys._MEIPASS, 'logo.png')
    config_data = load_config(config_path)
    bash_file = os.path.join(sys._MEIPASS, 'setup.sh')		
else:
    image_path = 'logo.png'
    config_data = load_config('.config')
    bash_file = 'setup.sh'
    config_path = ".config"

SECRET_KEY = config_data[0].encode()
PASSWORD_APP = config_data[1]
URL_USERNAME = config_data[2]
URL_PASSWORD = config_data[3]
ADV_USERNAME = config_data[4]
ADV_PASSWORD = config_data[5]

#test arumentów
try:
    if sys.argv[1] == "setup":
        subprocess.run(["bash", bash_file, str(pid), str(config_path)])
        exit()
except IndexError:
    pass

from PIL import Image
from urllib.parse import parse_qs
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http.cookies import SimpleCookie
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import time
import socketserver
import http.server
import mss
import io
import gc
import random
import ssl
import smtplib
import uuid
import base64

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "wifi.esp32@gmail.com"  # Twój e-mail
SENDER_PASSWORD = "hilh wkpm jtot rcze"  # Twoje hasło do e-maila

LOGIN_HTML = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="/icon.png" type="image/png">
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

VERYFICATION_HTML = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="/icon.png" type="image/png">
    <title>Weryfikacja</title>
</head>
<body>
    <h2>Wprowadź kod weryfikacyjny</h2>
    <form action="/verify" method="post">
        <label for="verification_code">Kod weryfikacyjny:</label>
        <input type="text" id="verification_code" name="verification_code" required>
        <br>
        <button type="submit">Zweryfikuj</button>
    </form>
</body>
</html>
"""

lista_uuid = []
lista_uuid_stream = []

class VideoStreamHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    global auth_ip
    global uuid_for_url_stream
    global ifDecCorrect
    global image_path
    auth_ip = []
    def do_GET(self):
        global cookie
        if self.path == "/auth/":
            cookie = SimpleCookie(self.headers.get('Cookie'))
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.clear_cookies()
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()

            self.wfile.write(LOGIN_HTML.encode('utf-8'))

        elif self.path == '/icon.png':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open(image_path, 'rb') as file:
                self.wfile.write(file.read())

        elif self.path == "/verify":
            # Sprawdź, czy użytkownik jest autoryzowany
            cookie = SimpleCookie(self.headers.get('Cookie'))
            if cookie.get('authenticated') and cookie['authenticated'].value in lista_uuid:
                self.send_response(200)

                self.send_header('Content-Type', 'text/html')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()

                self.wfile.write(VERYFICATION_HTML.encode('utf-8'))
            else:
                self.send_response(302)
                self.send_header('Location', '/auth/')
                self.end_headers()

        elif self.path.startswith("/auth/"+URL_USERNAME+"/"+URL_PASSWORD):
            for i in auth_ip:
                print(f"in for. i: {i}")
                if (10 + i[1]) > time.time():
                    if i[0] == self.client_address[0]:
                        if self.path == "/auth/"+URL_USERNAME+"/"+URL_PASSWORD+"/"+i[2]:
                            print(f"authorized. deleting: {i}")
                            auth_ip.remove(i)
                            self.send_response(200)
                            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
                            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                            self.send_header('Pragma', 'no-cache')
                            self.send_header('Expires', '0')
                            self.end_headers()
                            self.stream()
                        else:
                            print("ip address authorised but password doesn't much. deleting")
                            auth_ip.remove(i)
                    else:
                        self.send_response(401)
                        self.end_headers()
                else:
                    print("timeout detected")
                    auth_ip.remove(i)

        elif self.path == "/stream":
            cookie = SimpleCookie(self.headers.get('Cookie'))
            if cookie.get('acceptStream') and cookie['acceptStream'].value in lista_uuid_stream:
                self.send_response(200)
                self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.clear_cookies()
                self.end_headers()
                self.stream()
            else:
                self.send_response(302)
                self.send_header('Location', '/auth/')
                self.end_headers()
        else:
            pass

    def do_POST(self):
        global verification_code  # Dodaj tę linię, aby zadeklarować zmienną jako globalną
        if self.path == "/postauth":
            if True:#try:
                # Pobranie długości danych w żądaniu
                content_length = int(self.headers.get('Content-Length', 0))
                
                # Odczytanie danych
                post_data = self.rfile.read(content_length)
                post_text = post_data.decode('utf-8')  # Dekodowanie bajtów na string
                
                print("Odebrane dane zaszyfrowane: ", post_text)
                print("Typ danych: ", type(post_text))
                ifDecCorrect = True
                decrypted_password = self.decrypt_password(post_text)
                
                if ifDecCorrect == True:
                    print("Rozszyfrowane dane: ",decrypted_password)
                    print("Typ danych: ", type(decrypted_password))
                    ifDecCorrect = (decrypted_password == PASSWORD_APP)
                print("Czy zgodność haseł: ",str(ifDecCorrect))
                uuid_for_url_stream = uuid.uuid4().hex[:24]
                if ifDecCorrect == True:
                    auth_ip.append([self.client_address[0],time.time(),uuid_for_url_stream])
                    print(auth_ip)

                # Odpowiedź do klienta
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                if ifDecCorrect == True:
                    self.wfile.write(uuid_for_url_stream.encode('utf-8'))
                else:
                    self.wfile.write(b'ok')  # Odesłanie odpowiedzi

            """except Exception as e:
                self.send_response(400)  # Błąd żądania
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"Błąd: {str(e)}".encode("utf-8"))
                print("Błąd w obsłudze POST:", e)"""
        elif self.path == "/auth":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            fields = parse_qs(post_data)
            username = fields.get("username", [""])[0]
            password = fields.get("password", [""])[0]
            if username == ADV_USERNAME and password == ADV_PASSWORD:
                verification_code = self.generate_verification_code()
                self.send_verification_email(ADV_USERNAME, verification_code)
                special_uuid = str(uuid.uuid4())
                # Ustaw cookie po udanej autoryzacji
                self.send_response(302)
                self.send_header('Location', '/verify')
                self.send_header('Set-Cookie', f"authenticated={special_uuid}; Path=/")
                self.end_headers()
                lista_uuid.append(special_uuid)
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(LOGIN_HTML.encode('utf-8'))

        elif self.path == "/verify":
            cookie = SimpleCookie(self.headers.get('Cookie'))

            if cookie.get('authenticated') and cookie['authenticated'].value in lista_uuid:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                fields = parse_qs(post_data)
                entered_code = fields.get("verification_code", [""])[0]

                # Sprawdzamy, czy wprowadzony kod jest poprawny
                if entered_code == verification_code:
                    self.send_response(302)
                    self.send_header('Location', '/stream')
                    self.clear_cookie("authenticated")
                    special_uuid_stream = str(uuid.uuid4())
                    self.send_header('Set-Cookie', f"acceptStream={special_uuid_stream}; Path=/")
                    self.end_headers()
                    lista_uuid_stream.append(special_uuid_stream)

                else:
                    # Jeśli kod jest niepoprawny, wyświetlamy komunikat o błędzie
                    self.send_response(401)
                    self.send_header('Content-Type', 'text/html')
                    self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Expires', '0')
                    self.end_headers()
                    self.wfile.write(VERYFICATION_HTML.encode('utf-8'))
            else:
                self.send_response(302)
                self.send_header('Location', '/auth/')
                self.end_headers()

    def do_OPTIONS(self):
        """Obsługa zapytań preflight CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-thods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def decrypt_password(self, encrypted_password):
        try:
            # Zaszyfrowane hasło przychodzi jako base64 (AES)
            encrypted_password_bytes = base64.b64decode(encrypted_password)
        
            # Inicjowanie AES do deszyfrowania
            cipher = AES.new(SECRET_KEY, AES.MODE_CBC, SECRET_KEY)  # Używamy tego samego IV
            decrypted_bytes = unpad(cipher.decrypt(encrypted_password_bytes), AES.block_size)
        
            return decrypted_bytes.decode('utf-8')
        except ValueError:
            ifDecCorrect = False
            return

    def clear_cookies(self):
        cookie['authenticated'] = ''
        cookie['authenticated']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        cookie['authenticated']['path'] = '/'
        cookie['authenticated']['max-age'] = 0
        # Ustawienie ciasteczek do wygaszenia
        cookie['acceptStream'] = ''
        cookie['acceptStream']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        cookie['acceptStream']['path'] = '/'
        cookie['acceptStream']['max-age'] = 0
        # Wysyłanie nagłówków do wyczyszczenia ciastecz
        self.send_header('Set-Cookie', cookie.output(header="", sep="").strip())

    def clear_cookie(self,cookie_name):
        if cookie_name == "authenticated":
            cookie['authenticated'] = ''
            cookie['authenticated']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
            cookie['authenticated']['path'] = '/'
            cookie['authenticated']['max-age'] = 0
        elif cookie_name == "acceptStream":
            cookie['acceptStream'] = ''
            cookie['acceptStream']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
            cookie['acceptStream']['path'] = '/'
            cookie['acceptStream']['max-age'] = 0
        self.send_header('Set-Cookie', cookie.output().strip())

    def generate_verification_code(self):
        """Generuje losowy kod weryfikacyjny."""
        return "".join(map(str, random.sample(range(10), 6)))

    def send_verification_email(self, recipient_email, verification_code):
        """Wysyła e-mail z kodem weryfikacyjnym."""
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        current_time = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime())
        msg['Subject'] = f"{verification_code} - kod weryfikacyjny - {current_time}"

        body = f"<html><head></head><body><h2>Kod weryfikacyjny</h2><p>Twój kod weryfikacyjny to <b>{verification_code}</b>.</p><br></body></html>"
        msg.attach(MIMEText(body, "html"))

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            print("E-mail z kodem weryfikacyjnym został wysłany.")
        except Exception as e:
            print(f"Nie udało się wysłać e-maila: {e}")

    def stream(self):
        with mss.mss() as sct:
            while True:
                try:
                    start_time = time.time()
                    screenshot = sct.grab(sct.monitors[1])  # Pobiera cały ekran
    
                    # Konwersja do JPEG zamiast PNG (dużo szybsze)
                    img_byte_arr = io.BytesIO()
                    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
    
                    # Zmniejszamy rozdzielczość dla wydajności (np. 50% oryginału)
                    img = img.resize((screenshot.width // 2, screenshot.height // 2))
    
                    # Zapis do JPEG z kompresją
                    img.save(img_byte_arr, format='JPEG', quality=50)
                    img_byte_arr.seek(0)
    
                    self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Expires', '0')

                    self.end_headers()
    
                    # Wysyłanie klatek
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                    self.wfile.write(img_byte_arr.read())
                    self.wfile.write(b'\r\n')

                    print("czas: "+str(time.time() - start_time))
                    if (time.time() - start_time) < 0.14:
                        time.sleep(0.14 - (time.time() - start_time))  # 30 FPS
                    else:
                        time.sleep(0.05)
                    # Czyszczenie zmiennych img i img_byte_arr
                    img.close()
                    img_byte_arr.close()
    
                    # Wymuszenie usunięcia nieużywanych obiektów
                    gc.collect()
                except BrokenPipeError as e:
                    print(e)
                    break 

class VideoStreamServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

def run(port=8080):
    server_address = ('127.125.150.175', port)
    httpd = VideoStreamServer(server_address, VideoStreamHTTPRequestHandler)
    print(f"Serwer działa na porcie {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    verification_code = ""  # Inicjalizacja zmiennej globalnej
    run()
