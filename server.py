from flask import Flask, render_template, request
from bot_telegram import iniciar_bot, parar_bot

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('controle.html')

@app.route('/bot', methods=['POST'])
def bot_controller():
    acao = request.form.get('acao')
    if acao == 'start':
        iniciar_bot()
    elif acao == 'stop':
        parar_bot()
    return render_template('controle.html', status=acao)
