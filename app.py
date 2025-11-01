"""
AFS Cloud Live Monitor
Mini-app Flask conectada a Ubidots (versión compatible con cuenta gratuita / BBUS)
Versión 1.1 – FASE 2 (2025)
Autor: Aqua Feelings Systems (AF Systems)
"""

from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

# === Variables de entorno ===
UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
DEVICE_LABEL = os.getenv("DEVICE_LABEL", "afs_piloto")

# Endpoint para cuentas gratuitas (API v1.6)
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"

VARIABLES = [
    "nivel_agua",
    "caudal",
    "eficiencia",
    "balance_hidrico",
    "lluvia"
]


# === Función para obtener datos desde Ubidots ===
def obtener_datos():
    datos = {}
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}

    try:
        res = requests.get(UBIDOTS_URL, headers=headers, timeout=5)
        if res.status_code == 200:
            info = res.json()
            print("✅ Datos recibidos desde Ubidots:")
            print(info)  # Log para depurar

            for var in VARIABLES:
                valor = (
                    info.get(var, {})
                    .get("last_value", {})
                    .get("value", None)
                )
                datos[var] = round(valor, 2) if valor is not None else None
        else:
            print(f"⚠️ Error {res.status_code} al obtener datos: {res.text}")
            for var in VARIABLES:
                datos[var] = None

    except Exception as e:
        print(f"❌ Error en la conexión con Ubidots: {e}")
        for var in VARIABLES:
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


# === Ejecución principal ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


