import requests
from bs4 import BeautifulSoup
from telegram import Bot
import os
import asyncio

# URL de la página web que queremos consultar
url = "https://www.lapelotona.com/partidos-de-futbol-para-hoy-en-vivo/"

# Reemplaza con el token de tu bot de Telegram
#TELEGRAM_BOT_TOKEN = ''
# Reemplaza con el ID del chat al que quieres enviar los mensajes
#TELEGRAM_CHAT_ID = '-323606418'

# Lista de ligas que nos interesan (en minúsculas para hacer la comparación insensible a mayúsculas)
LIGAS_INTERES = [
    "la liga ea sports",
    "serie a italiana",
    "bundesliga",
    "premier league",
    "liga betplay dimayor",
    "copa sudamericana",
    "copa libertadores"
]

async def enviar_mensaje_telegram(bot, chat_id, partidos_filtrados):
    mensaje_base = "⚽️ Futbol para hoy ⚽️\n\n"
    mensaje_actual = mensaje_base
    mensajes_a_enviar = []

    if partidos_filtrados:
        for partido in partidos_filtrados:
            info_partido = f"Partido: {partido['equipos']}\n"
            info_partido += f"Hora: {partido['hora']}\n"
            info_partido += f"Liga: {partido['liga']}\n"
            info_partido += f"Canales: {partido['canales']}\n"
            info_partido += "------------------------------\n"

            if len(mensaje_actual) + len(info_partido) <= 4096:
                mensaje_actual += info_partido
            else:
                mensajes_a_enviar.append(mensaje_actual)
                mensaje_actual = mensaje_base + info_partido
        mensajes_a_enviar.append(mensaje_actual) # Añadir el último mensaje

        for mensaje in mensajes_a_enviar:
            try:
                await bot.send_message(chat_id=chat_id, text=mensaje) # <--- Usa los argumentos
                print("Mensaje enviado a Telegram.")
                await asyncio.sleep(0.1) # Pequeña pausa para evitar rate limiting
            except Exception as e:
                print(f"Error al enviar mensaje a Telegram: {e}")
                break
    else:
        try:
            await bot.send_message(chat_id=chat_id, text=mensaje_base + "No se encontraron partidos de las ligas seleccionadas para hoy.") # <--- Usa los argumentos
            print("Mensaje enviado a Telegram.")
        except Exception as e:
            print(f"Error al enviar el mensaje a Telegram: {e}")

def extraer_datos_partidos():
    try:
        # Realizar la petición GET a la página web
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la petición falla

        # Crear el objeto BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar la tabla de partidos por su ID
        tabla_partidos = soup.find('table', {'id': 'partidos-hoy'})

        partidos_filtrados = []

        if tabla_partidos:
            filas_partidos = tabla_partidos.find_all('tr')[1:]  # Omitir la primera fila (encabezado)

            for fila in filas_partidos:
                celda_equipos = fila.find('td', {'class': 'equipos'})
                celda_fecha = fila.find('td', {'class': 'fecha'})

                if celda_equipos and celda_fecha:
                    equipos = [span.get_text(strip=True) for span in celda_equipos.find_all('span')]
                    hora = celda_fecha.find('span', {'class': 'usa-time'}).get_text(strip=True) if celda_fecha.find('span', {'class': 'usa-time'}) else "Hora no encontrada"
                    liga_canales_texto = celda_fecha.get_text(separator='<br>').split('<br>')
                    liga_canales = [texto.strip() for texto in liga_canales_texto if texto.strip()]

                    liga = "Liga no encontrada"
                    canales = "Canales no encontrados"

                    if len(liga_canales) > 1:
                        info_liga_canal = liga_canales[1].split(' - ')
                        if len(info_liga_canal) >= 2:
                            liga = info_liga_canal[0].strip().lower() # Convertir a minúsculas para comparar
                            canales = ', '.join([canal.strip() for canal in info_liga_canal[1:]])
                        elif len(info_liga_canal) == 1:
                            liga = info_liga_canal[0].strip().lower() # Convertir a minúsculas para comparar
                            canales = "No se encontraron canales"
                    elif len(liga_canales) == 1:
                        liga = liga_canales[0].strip().lower() # Convertir a minúsculas para comparar
                        canales = "No se encontraron canales"

                    # Filtrar por las ligas de interés
                    if liga in LIGAS_INTERES:
                        partido = {
                            'equipos': ' vs '.join(equipos),
                            'hora': hora,
                            'liga': liga.title(), # Mostrar la liga con la primera letra en mayúscula
                            'canales': canales
                        }
                        partidos_filtrados.append(partido)
            return partidos_filtrados
        else:
            print("No se encontró la tabla de partidos con el ID 'partidos-hoy'.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la página web: {e}")
        return []
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return []

"""def main(event, context):
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("-323606418")

    if not telegram_token or not telegram_chat_id:
        print("Error: Variables de entorno TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configuradas.")
        return

    bot = Bot(token=telegram_token)
    datos_partidos = extraer_datos_partidos()
    if datos_partidos:
        asyncio.run(enviar_mensaje_telegram(bot, telegram_chat_id, datos_partidos))
        print("Función ejecutada y mensaje (o mensajes) enviados a Telegram.")
    else:
        print("No se encontraron partidos para las ligas seleccionadas.")
"""
# main.py
def main(event, context):
    print("Simple Cloud Run function started successfully.")
    return "OK"

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    local_telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    local_telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if local_telegram_token and local_telegram_chat_id:
        datos_partidos = extraer_datos_partidos()
        if datos_partidos:
            asyncio.run(enviar_mensaje_telegram(Bot(token=local_telegram_token), local_telegram_chat_id, datos_partidos))
    else:
        print("Advertencia: Variables de entorno para Telegram no configuradas localmente. El script en Cloud Functions las usará.")
