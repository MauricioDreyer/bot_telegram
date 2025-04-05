import re
from telethon import TelegramClient, events
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNEL = int(os.getenv("SOURCE_CHANNEL"))
DESTINATION_CHANNEL = int(os.getenv("DESTINATION_CHANNEL"))


# Criando o cliente do bot
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Caminho das imagens de fundo
IMG_FUNDO_LONG = "img_fundo_B.png"
IMG_FUNDO_SHORT = "img_fundo_S.png"

# Definir a fonte Arial
try:
    FONTE_PATH = "C:/Windows/Fonts/Arial.ttf"  # Caminho para Windows
    FONTE_TAMANHO = 40
    fonte = ImageFont.truetype(FONTE_PATH, FONTE_TAMANHO)
except OSError:
    print("Fonte Arial não encontrada, usando fonte padrão.")
    fonte = ImageFont.load_default()

def formatar_numero(valor, casas_decimais=2):
    """
    Formata os números para o padrão correto:
    - Usa ponto como separador de milhar
    - Usa vírgula como decimal
    - Mantém o número correto de casas decimais
    """
    try:
        valor = float(valor.replace(".", "").replace(",", "."))  # Corrige entrada
        return f"{valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return "N/A"

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handle_new_message(event):
    mensagem = event.raw_text
    print("Nova mensagem recebida:", mensagem)
    
    nome_arquivo = gerar_imagem_sinal(mensagem)
    
    if nome_arquivo:
        await client.send_file(DESTINATION_CHANNEL, nome_arquivo, caption="📊 Novo sinal de trade recebido!")
        print("Imagem enviada para o canal de destino!")

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
    
    # Extração de dados
    par = re.search(r"Pair:\s*([A-Z]+USDT)", mensagem)
    roi = re.search(r"ROI:\s*(-?\d+,?\d*)%", mensagem)
    pnl = re.search(r"PNL:\s*(-?\d+,?\d*)", mensagem)
    size = re.search(r"Size:\s*(\d+,?\d*)", mensagem)
    margin = re.search(r"Margin:\s*(\d+,?\d*)", mensagem)
    margin_ratio = re.search(r"Margin Ratio:\s*(-?\d+,?\d*)%", mensagem)
    entry_price = re.search(r"Entry Price:\s*(\d+[.,]?\d*)", mensagem)
    mark_price = re.search(r"Mark Price:\s*(\d+[.,]?\d*)", mensagem)
    liq_price = re.search(r"Liq Price:\s*(\d+[.,]?\d*)", mensagem)
    
    # Pegando valores ou definindo padrão
    par = par.group(1) if par else "N/A"
    roi_value = formatar_numero(roi.group(1)) if roi else "0,00"
    pnl_value = formatar_numero(pnl.group(1)) if pnl else "0,00"
    margin_ratio_value = formatar_numero(margin_ratio.group(1)) if margin_ratio else "0,00"
    
    size = formatar_numero(size.group(1), 3) if size else "N/A"  # 3 casas decimais para Size
    margin = formatar_numero(margin.group(1)) if margin else "N/A"
    entry_price = formatar_numero(entry_price.group(1)) if entry_price else "N/A"
    mark_price = formatar_numero(mark_price.group(1)) if mark_price else "N/A"
    liq_price = formatar_numero(liq_price.group(1)) if liq_price else "N/A"
    
    roi_cor = cor_verde if float(roi_value.replace(",", ".")) >= 0 else cor_vermelha
    pnl_cor = cor_verde if float(pnl_value.replace(",", ".")) >= 0 else cor_vermelha
    margin_ratio_cor = cor_verde if float(margin_ratio_value.replace(",", ".")) >= 0 else cor_vermelha
    
    # Função para alinhar à direita
    def alinhar_direita(texto, x_final, y, cor=cor_branca):
        text_width = draw.textbbox((0, 0), texto, font=fonte)[2]
        draw.text((x_final - text_width, y), texto, font=fonte, fill=cor)

    # Posicionamento dos textos
    # Criar uma fonte maior para o Pair
    FONTE_GRANDE_TAMANHO = 60
    fonte_grande = ImageFont.truetype(FONTE_PATH, FONTE_GRANDE_TAMANHO)

    # Escrever o Pair com fonte maior
    draw.text((100, 45), f"{par}", font=fonte_grande, fill=cor_branca)

    alinhar_direita(f"{roi_value}%", 1135, 220, roi_cor)  # ROI alinhado à direita
    draw.text((50, 220), f"{pnl_value}", font=fonte, fill=pnl_cor)  # PNL normal
    draw.text((50, 360), f"{size}", font=fonte, fill=cor_branca)  # Size normal
    draw.text((420, 360), f"{margin}", font=fonte, fill=cor_branca)  # Margin normal
    alinhar_direita(f"{margin_ratio_value}%", 1135, 360, margin_ratio_cor)  # Margin Ratio alinhado à direita
    draw.text((50, 500), f"{entry_price}", font=fonte, fill=cor_branca)  # Entry Price normal
    draw.text((420, 500), f"{mark_price}", font=fonte, fill=cor_branca)  # Mark Price normal
    alinhar_direita(f"{liq_price}", 1135, 500)  # Liq Price alinhado à direita

    img_fundo.save(nome_arquivo)
    print(f"Imagem salva como {nome_arquivo}")
    return nome_arquivo

print("Bot rodando...")
client.run_until_disconnected()
