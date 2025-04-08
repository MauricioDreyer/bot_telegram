from flask import Flask, jsonify
from bot_telegram import start_bot, stop_bot, is_bot_running

app = Flask(__name__)

@app.route("/")
def home():
    return "Painel do bot ativo! Use /start, /stop ou /status para controlar o bot."

@app.route("/start")
def start():
    if is_bot_running():
        return jsonify({"status": "Bot já está em execução."})
    start_bot()
    return jsonify({"status": "Bot iniciado com sucesso."})

@app.route("/stop")
def stop():
    if not is_bot_running():
        return jsonify({"status": "Bot já está parado."})
    stop_bot()
    return jsonify({"status": "Bot parado com sucesso."})

@app.route("/status")
def status():
    status = "ativo" if is_bot_running() else "parado"
    return jsonify({"status": f"Bot está {status}."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
