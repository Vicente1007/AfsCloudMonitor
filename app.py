import os
import threading
import time
import requests
from flask import Flask, render_template, jsonify

# ============================================================
# 🌎 CONFIGURACIÓN GENERAL
# ============================================================

app = Flask(__name__)

UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
DEVICE_LABEL = os.getenv("DEVICE_LABEL", "afs_piloto")
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"

# Intervalo de simulación (segundos)
SIM_INTERVAL = 30


# ============================================================
# 🔧 FUNCIONES PRINCIPALES
# ============================================================

def obtener_datos():
    """Obtiene las últimas lecturas desde Ubidots."""
    try:
        headers = {"X-Auth-Token": UBIDOTS_TOKEN}
        response = requests.get(UBIDOTS_URL, headers=headers, timeout=10)
        data = response.json()

        return {
            "nivel_agua": round(data.get("nivel_agua", {}).get("value", 0), 2),
            "caudal": round(data.get("caudal", {}).get("value", 0), 2),
            "eficiencia": round(data.get("eficiencia", {}).get("value", 0), 2),
            "balance_hidrico": round(data.get("balance_hidrico", {}).get("value", 0), 2),
            "lluvia": round(data.get("lluvia", {}).get("value", 0), 2),
        }

    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error al obtener datos: {e}")
        return {"nivel_agua": 0, "caudal": 0, "eficiencia": 0, "balance_hidrico": 0, "lluvia": 0}


def enviar_datos():
    """Envía datos simulados a Ubidots (modo automático)."""
    try:
        payload = {
            "nivel_agua": round(0.5 + (time.time() % 2.5), 2),
            "caudal": round(0.2 + (time.time() % 1.5), 2),
            "eficiencia": round(75 + (time.time() % 20), 2),
            "balance_hidrico": round(-100 + (time.time() % 50), 2),
            "lluvia": round((time.time() % 2) / 2, 2)
        }

        headers = {
            "X-Auth-Token": UBIDOTS_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.post(UBIDOTS_URL, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 📤 Datos enviados: {payload}")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Error {response.status_code} al enviar: {response.text}")

    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Error al enviar datos: {e}")


def ciclo_automatico():
    """Envío continuo cada X segundos."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🔁 Ciclo automático iniciado ({SIM_INTERVAL}s intervalos)")
    while True:
        enviar_datos()
        time.sleep(SIM_INTERVAL)


# ============================================================
# 🌐 ENDPOINTS FLASK
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(obtener_datos())

@app.route("/simulate")
def simulate():
    enviar_datos()
    return jsonify({"status": "ok", "msg": "Datos simulados enviados manualmente."})


# ============================================================
# 🚀 EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    print("🚀 AFS Cloud Monitor iniciado en modo PRO (automático cada 30 s).")
    hilo = threading.Thread(target=ciclo_automatico, daemon=True)
    hilo.start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))


