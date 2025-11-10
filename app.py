import os
import requests
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # ✅ Permite que el HTML acceda a /data sin bloqueo CORS

# Variables de entorno
UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
DEVICE_LABEL = os.getenv("DEVICE_LABEL", "afs_piloto")

UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    """Obtiene los datos de Ubidots y los entrega al dashboard visual."""
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}

    try:
        response = requests.get(UBIDOTS_URL, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"[{datetime.now()}] ⚠️ Error Ubidots {response.status_code}: {response.text}")
            return jsonify({
                "nivel_agua": 0, "caudal": 0, "eficiencia": 0,
                "balance_hidrico": 0, "lluvia": 0
            })

        data = response.json()

        # Mapea las variables del dispositivo
        result = {
            "nivel_agua": data.get("nivel_agua", {}).get("value", 0),
            "caudal": data.get("caudal", {}).get("value", 0),
            "eficiencia": data.get("eficiencia", {}).get("value", 0),
            "balance_hidrico": data.get("balance_hidrico", {}).get("value", 0),
            "lluvia": data.get("lluvia", {}).get("value", 0)
        }

        print(f"[{datetime.now()}] ✅ Datos enviados a /data → {result}")
        return jsonify(result)

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error general: {e}")
        return jsonify({
            "nivel_agua": 0, "caudal": 0, "eficiencia": 0,
            "balance_hidrico": 0, "lluvia": 0
        })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

    
