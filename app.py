"""
💧 AFS Cloud Live Monitor – Fase Piloto (Render Free)
Monitoreo técnico en tiempo real – Aqua Feelings Systems
Versión 1.1 – Endpoint de simulación habilitado
"""

from flask import Flask, render_template, jsonify
import requests
import os
import random

# ---------------------------
# 🔧 Configuración inicial
# ---------------------------

app = Flask(__name__)

# Variables de entorno configuradas en Render
UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
DEVICE_LABEL = os.getenv("DEVICE_LABEL", "afs_piloto")
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v2.0/devices/{DEVICE_LABEL}/"
HEADERS = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}

# Variables monitoreadas (mismo nombre API label en Ubidots)
VARIABLES = [
    "nivel_agua",
    "caudal",
    "eficiencia",
    "balance_hidrico",
    "lluvia"
]

# ---------------------------
# 🧠 Función para obtener datos reales desde Ubidots
# ---------------------------
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


# ---------------------------
# 🌍 Rutas principales
# ---------------------------

@app.route('/')
def index():
    """Página principal con dashboard."""
    return render_template('dashboard.html')


@app.route('/data')
def data():
    """Entrega los valores actuales a la interfaz web."""
    datos = obtener_datos()
    return jsonify(datos)


# ---------------------------
# 🧩 Endpoint de simulación (para plan gratuito)
# ---------------------------

@app.route('/simulate')
def simulate():
    """
    Genera lecturas simuladas y las envía a Ubidots.
    Se puede ejecutar manualmente o con un cron externo cada 1 minuto.
    """
    payload = {
        "nivel_agua": round(random.uniform(10, 100), 2),
        "caudal": round(random.uniform(0.5, 3.5), 2),
        "eficiencia": round(random.uniform(60, 95), 2),
        "balance_hidrico": round(random.uniform(-200, 1200), 2),
        "lluvia": round(random.uniform(0, 5), 2)
    }

    try:
        res = requests.post(UBIDOTS_URL, headers=HEADERS, json=payload, timeout=5)
        if res.status_code == 201:
            return {"status": "ok", "data": payload, "source": "simulate"}
        else:
            return {"status": "error", "code": res.status_code, "response": res.text}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ---------------------------
# 🔥 Ejecución local
# ---------------------------

if __name__ == '__main__':
    # En el plan gratuito NO se usa threading.
    # Si luego pasas al plan Pro, aquí se puede reactivar la simulación automática:
    #
    # import threading
    # threading.Thread(target=generar_datos, daemon=True).start()
    #
    app.run(host='0.0.0.0', port=5000)

