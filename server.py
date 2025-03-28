from flask import Flask
import subprocess

app = Flask(__name__)

bot_process = None

@app.route("/start")
def start_bot():
    global bot_process
    if bot_process is None:
        bot_process = subprocess.Popen(["python", "bot_telegram.py"])
        return "Bot iniciado!", 200
    return "Bot já está rodando!", 200

@app.route("/stop")
def stop_bot():
    global bot_process
    if bot_process is not None:
        bot_process.terminate()
        bot_process = None
        return "Bot parado!", 200
    return "Bot não está rodando!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
