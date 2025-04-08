from flask import Flask, jsonify, render_template, request, redirect, url_for
from bot_telegram import iniciar_bot, parar_bot, is_bot_running

app = Flask(__name__)

@app.route("/")
def home():
    status = "Ativo" if is_bot_running() else "Parado"
    return render_template("controle.html", status=status)

@app.route("/bot", methods=["POST"])
def bot_control():
    acao = request.form.get("acao")
    if acao == "start":
        if not is_bot_running():
            iniciar_bot()
    elif acao == "stop":
        if is_bot_running():
            parar_bot()
    return redirect(url_for("home"))

@app.route("/status")
def status():
    status = "ativo" if is_bot_running() else "parado"
    return jsonify({"status": f"Bot está {status}."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
