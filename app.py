"""
AFS Cloud Live Monitor
Mini-app Flask conectada a Ubidots
Versión 1.0 – FASE 2 (2025)
Autor: Aqua Feelings Systems (AF Systems)
"""

from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

# === Configuración Ubidots ===
UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
DEVICE_LABEL = os.getenv("DEVICE_LABEL", "AFS_Piloto")
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v2.0/devices/{DEVICE_LABEL}/"
HEADERS = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}

# === Variables disponibles ===
VARIABLES = [
    "nivel_agua",
    "caudal",
    "eficiencia",
    "balance_hidrico",
    "lluvia"
]

# === Función para obtener los últimos valores ===
def obtener_datos():
    datos = {}
    for var in VARIABLES:
        try:
            url = f"{UBIDOTS_URL}{var}/values/?page_size=1"
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 200 and res.json().get("results"):
                valor = res.json()["results"][0]["value"]
                datos[var] = round(valor, 2)
            else:
                datos[var] = None
        except Exception:
            datos[var] = None
    return datos

# === Rutas Flask ===
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/data')
def data():
    datos = obtener_datos()
    return jsonify(datos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

