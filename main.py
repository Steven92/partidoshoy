import requests
from bs4 import BeautifulSoup
from telegram import Bot
import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler

# ... (Your existing code: LIGAS_INTERES, enviar_mensaje_telegram, extraer_datos_partidos) ...

def main(event, context):
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not telegram_token or not telegram_chat_id:
        print("Error: Variables de entorno no configuradas.")
        return

    bot = Bot(token=telegram_token)
    url = "https://www.lapelotona.com/partidos-de-futbol-para-hoy-en-vivo/"
    datos_partidos = extraer_datos_partidos(url)
    if datos_partidos:
        asyncio.run(enviar_mensaje_telegram(bot, telegram_chat_id, datos_partidos))
        print("Función ejecutada y mensaje (o mensajes) enviados a Telegram.")
    else:
        print("No se encontraron partidos para las ligas seleccionadas.")

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

def run_health_check_server():
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    import threading
    # Run the main function in a separate thread (or directly if it's quick)
    threading.Thread(target=main, daemon=True).start()
    # Start the health check server in the main thread
    run_health_check_server()