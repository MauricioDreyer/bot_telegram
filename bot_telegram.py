import re
from telethon import TelegramClient, events
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv
import threading

load_dotenv()

# Suas credenciais do Telegram
API_ID = '20332810'
API_HASH = '2595744c1a58cb7fee8729d381439060'
BOT_TOKEN = '7686190005:AAFyHP2yCeYCyk1RbdxCPbfR-5_fh5yZTHA'

SOURCE_CHANNEL = 2429559430
DESTINATION_CHANNEL = 1002395741879

bot_ativo = False
client = None

def iniciar_bot():
    global bot_ativo, client
    if bot_ativo:
        print("Bot já está rodando.")
        return

    bot_ativo = True

    def bot_loop():
        global client
        client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

        @client.on(events.NewMessage(chats=SOURCE_CHANNEL))
        async def handle_new_message(event):
            mensagem = event.raw_text
            nome_arquivo = gerar_imagem_sinal(mensagem)
            if nome_arquivo:
                await client.send_file(DESTINATION_CHANNEL, nome_arquivo, caption="📊 Novo sinal de trade recebido!")

        print("Bot iniciado.")
        client.run_until_disconnected()

    threading.Thread(target=bot_loop).start()

def parar_bot():
    global bot_ativo, client
    if client:
        client.disconnect()
        client = None
    bot_ativo = False
    print("Bot parado.")

def is_bot_running():
    return bot_ativo

IMG_FUNDO_LONG = "img_fundo_B.png"
IMG_FUNDO_SHORT = "img_fundo_S.png"

try:
    FONTE_PATH = "C:/Windows/Fonts/Arial.ttf"
    FONTE_TAMANHO = 40
    fonte = ImageFont.truetype(FONTE_PATH, FONTE_TAMANHO)
except OSError:
    print("Fonte Arial não encontrada, usando fonte padrão.")
    fonte = ImageFont.load_default()

def formatar_numero(valor, casas_decimais=2):
    try:
        valor = float(valor.replace(".", "").replace(",", "."))
        return f"{valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return "N/A"

def gerar_imagem_sinal(mensagem, nome_arquivo="sinal_trade.png"):
    try:
        direcao = "LONG" if "LONG" in mensagem.upper() else "SHORT"
        img_fundo_path = IMG_FUNDO_LONG if direcao == "LONG" else IMG_FUNDO_SHORT
        img_fundo = Image.open(img_fundo_path)
        largura, altura = img_fundo.size
    except Exception as e:
        print(f"Erro ao carregar a imagem de fundo: {e}")
        return None

    draw = ImageDraw.Draw(img_fundo)
    cor_verde = (0, 255, 0)
    cor_vermelha = (255, 0, 0)
    cor_branca = (255, 255, 255)

    par = re.search(r"Pair:\s*([A-Z]+USDT)", mensagem)
    roi = re.search(r"ROI:\s*(-?\d+,?\d*)%", mensagem)
    pnl = re.search(r"PNL:\s*(-?\d+,?\d*)", mensagem)
    size = re.search(r"Size:\s*(\d+,?\d*)", mensagem)
    margin = re.search(r"Margin:\s*(\d+,?\d*)", mensagem)
    margin_ratio = re.search(r"Margin Ratio:\s*(-?\d+,?\d*)%", mensagem)
    entry_price = re.search(r"Entry Price:\s*(\d+[.,]?\d*)", mensagem)
    mark_price = re.search(r"Mark Price:\s*(\d+[.,]?\d*)", mensagem)
    liq_price = re.search(r"Liq Price:\s*(\d+[.,]?\d*)", mensagem)

    par = par.group(1) if par else "N/A"
    roi_value = formatar_numero(roi.group(1)) if roi else "0,00"
    pnl_value = formatar_numero(pnl.group(1)) if pnl else "0,00"
    margin_ratio_value = formatar_numero(margin_ratio.group(1)) if margin_ratio else "0,00"

    size = formatar_numero(size.group(1), 3) if size else "N/A"
    margin = formatar_numero(margin.group(1)) if margin else "N/A"
    entry_price = formatar_numero(entry_price.group(1)) if entry_price else "N/A"
    mark_price = formatar_numero(mark_price.group(1)) if mark_price else "N/A"
    liq_price = formatar_numero(liq_price.group(1)) if liq_price else "N/A"

    roi_cor = cor_verde if float(roi_value.replace(",", ".")) >= 0 else cor_vermelha
    pnl_cor = cor_verde if float(pnl_value.replace(",", ".")) >= 0 else cor_vermelha
    margin_ratio_cor = cor_verde if float(margin_ratio_value.replace(",", ".")) >= 0 else cor_vermelha

    def alinhar_direita(texto, x_final, y, cor=cor_branca):
        text_width = draw.textbbox((0, 0), texto, font=fonte)[2]
        draw.text((x_final - text_width, y), texto, font=fonte, fill=cor)

    FONTE_GRANDE_TAMANHO = 60
    fonte_grande = ImageFont.truetype(FONTE_PATH, FONTE_GRANDE_TAMANHO)

    draw.text((100, 45), f"{par}", font=fonte_grande, fill=cor_branca)

    alinhar_direita(f"{roi_value}%", 1135, 220, roi_cor)
    draw.text((50, 220), f"{pnl_value}", font=fonte, fill=pnl_cor)
    draw.text((50, 360), f"{size}", font=fonte, fill=cor_branca)
    draw.text((420, 360), f"{margin}", font=fonte, fill=cor_branca)
    alinhar_direita(f"{margin_ratio_value}%", 1135, 360, margin_ratio_cor)
    draw.text((50, 500), f"{entry_price}", font=fonte, fill=cor_branca)
    draw.text((420, 500), f"{mark_price}", font=fonte, fill=cor_branca)
    alinhar_direita(f"{liq_price}", 1135, 500)

    img_fundo.save(nome_arquivo)
    print(f"Imagem salva como {nome_arquivo}")
    return nome_arquivo