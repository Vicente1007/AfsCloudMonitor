"""
AFS Cloud Live Monitor – versión autosimulada
Render actúa como fuente y dashboard a la vez
"""

from flask import Flask, render_template, jsonify
import threading, time, requests, os, random

app = Flask(__name__)

# === CONFIGURACIÓN ===
UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
DEVICE_LABEL = os.getenv("DEVICE_LABEL", "afs_piloto")
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"

HEADERS = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}

VARIABLES = ["nivel_agua", "caudal", "eficiencia", "balance_hidrico", "lluvia"]

# === SIMULADOR DE DATOS ===
def generar_datos():
    """Ciclo permanente que genera y envía datos a Ubidots."""
    while True:
        try:
            payload = {
                "nivel_agua": random.uniform(40, 100),
                "caudal": random.uniform(0.5, 3.0),
                "eficiencia": random.uniform(70, 95),
                "balance_hidrico": random.uniform(200, 1000),
                "lluvia": random.uniform(0, 5)
            }
            res = requests.post(UBIDOTS_URL, headers=HEADERS, json=payload, timeout=5)
            print(f"[SIMULADOR] Enviados datos: {payload} | Respuesta {res.status_code}")
        except Exception as e:
            print("[SIMULADOR] Error:", e)
        time.sleep(60)  # cada 60 segundos

# === LECTOR DE DATOS PARA DASHBOARD ===
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

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/data')
def data():
    datos = obtener_datos()
    return jsonify(datos)

# === INICIO AUTOMÁTICO DEL SIMULADOR ===
if __name__ == '__main__':
    threading.Thread(target=generar_datos, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
