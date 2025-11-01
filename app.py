
import os
import threading
import time
import requests
from flask import Flask, render_template, jsonify

# ============================================================
# 🌎 CONFIGURACIÓN GENERAL
# ============================================================

app = Flask(__name__)

# Variables de entorno
UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
DEVICE_LABEL = os.getenv("DEVICE_LABEL", "afs_piloto")
MODE = os.getenv("MODE", "free").lower()  # "free" o "pro"

UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"

# ============================================================
# 🔧 FUNCIONES PRINCIPALES
# ============================================================

def obtener_datos():
    """
    Obtiene las últimas lecturas desde Ubidots.
    """
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
        print(f"❌ Error al obtener datos: {e}")
        return {"nivel_agua": 0, "caudal": 0, "eficiencia": 0, "balance_hidrico": 0, "lluvia": 0}


def enviar_datos():
    """
    Envía datos simulados a Ubidots (solo para modo demostración).
    """
    try:
        payload = {
            "nivel_agua": round(2 + 3 * time.time() % 10, 2),
            "caudal": round(1 + 2 * time.time() % 5, 2),
            "eficiencia": round(75 + (time.time() % 5), 2),
            "balance_hidrico": round(-120 + (time.time() % 10), 2),
            "lluvia": round(0.1 + (time.time() % 2) / 10, 2)
        }

        headers = {
            "X-Auth-Token": UBIDOTS_TOKEN,
            "Content-Type": "application/json"
        }

        requests.post(UBIDOTS_URL, headers=headers, json=payload, timeout=10)
        print(f"📤 Datos enviados a Ubidots: {payload}")

    except Exception as e:
        print(f"⚠️ Error al enviar datos: {e}")


def ciclo_automatico():
    """
    Genera lecturas automáticas cada 60 segundos (modo PRO).
    """
    while True:
        enviar_datos()
        time.sleep(60)


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
    if MODE == "pro":
        print("🚀 AFS Cloud Monitor iniciado en modo PRO (automático cada 1 min).")
        hilo = threading.Thread(target=ciclo_automatico, daemon=True)
        hilo.start()
    else:
        print("⚠️ Modo FREE: ejecuta /simulate manualmente o usa cron-job.org.")

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

