import re
from telethon import TelegramClient, events
from PIL import Image, ImageDraw, ImageFont

# Suas credenciais do Telegram
API_ID = '20332810'
API_HASH = '2595744c1a58cb7fee8729d381439060'
BOT_TOKEN = '7686190005:AAFyHP2yCeYCyk1RbdxCPbfR-5_fh5yZTHA'

# ID do canal de origem (de onde o bot vai pegar as mensagens)
SOURCE_CHANNEL = 2429559430  
# ID do canal de destino (para onde o bot enviará as imagens)  
DESTINATION_CHANNEL = 1002395741879

# Criando o cliente do bot
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Caminho da imagem de fundo
IMG_FUNDO_PATH = "img_fundo.png"

# Evento para capturar novas mensagens no canal
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handle_new_message(event):
    mensagem = event.raw_text
    print("Nova mensagem recebida:", mensagem)

    # Gerar imagem com o texto capturado
    nome_arquivo = gerar_imagem_sinal(mensagem)

    if nome_arquivo:
        # Enviar a imagem para o canal de destino
        await client.send_file(DESTINATION_CHANNEL, nome_arquivo, caption="📊 Novo sinal de trade recebido!")
        print("Imagem enviada para o canal de destino!")

def gerar_imagem_sinal(mensagem, nome_arquivo="sinal_trade.png"):
    try:
        # Carregar imagem de fundo
        img_fundo = Image.open(IMG_FUNDO_PATH)
        largura, altura = img_fundo.size
    except Exception as e:
        print(f"Erro ao carregar a imagem de fundo: {e}")
        return None

    draw = ImageDraw.Draw(img_fundo)

    # Determinar se é LONG ou SHORT
    if "SHORT" in mensagem.upper():
        direcao = "SHORT"
        cor_destaque = (255, 0, 0)  # Vermelho
    elif "LONG" in mensagem.upper():
        direcao = "LONG"
        cor_destaque = (0, 255, 0)  # Verde
    else:
        direcao = "Desconhecido"
        cor_destaque = (255, 255, 255)  # Branco

    # Definição das fontes
    try:
        fonte_titulo = ImageFont.truetype("Orbitron-Bold.ttf", 100)
        fonte_texto = ImageFont.truetype("Orbitron-Bold.ttf", 60)
    except:
        fonte_titulo = ImageFont.load_default()
        fonte_texto = ImageFont.load_default()

    # Extraindo dados da mensagem
    par_cripto = re.search(r"([A-Z]+/[A-Z]+)", mensagem)  # Exemplo: "DOGE/USDT"
    alavancagem = re.search(r"LEVERAGE\s*[:|-]?\s*Cross\s*(\d+)X", mensagem, re.IGNORECASE)  # Exemplo: "20X"
    entrada = re.search(r"ENTRY\s*[:|-]?\s*([\d,\.]+)\s*-\s*([\d,\.]+)", mensagem)  # Exemplo: "0.16938 - 0.16954"
    # Ajuste para Stop Loss
    # Modificação para capturar Stop Loss em porcentagem (ex: "5%-10%")
    stop_loss_decimal = re.search(r"Stop\s*Loss\s*[:|-]?\s*([\d,\.]+)", mensagem)  # Exemplo: "0.155976"
    stop_loss_percent = re.search(r"Stop\s*Loss\s*[:|-]?\s*(\d+%-\d)", mensagem)  # Exemplo: "5%-10%"
    
    # Identificar qual formato de Stop Loss está presente
    if stop_loss_percent:
        stop_loss = "5% - 10%"  # Valor fixo para porcentagem
    elif stop_loss_decimal:
        stop_loss = stop_loss_decimal.group(1)  # Exemplo: "0.155976"
    else:
        stop_loss = "Desconhecido"
    # Identificar os tipos de Take Profits
    take_profit_target = re.findall(r"TARGET\s*\d+\s*[-:]*\s*([\d,\.]+)", mensagem) # Exemplo: " TARGET 1 - 8.39"
    take_profit_tp = re.findall(r"\d+\)\s*:?\s*([\d,\.]+)", mensagem) # Exemplo: "1) : 0.2095"

    if take_profit_target:
        take_profits = take_profit_target
    elif take_profit_tp:
        take_profits = take_profit_tp
    else:
        take_profits = "Desconhecido"

    # Tratamento das informações extraídas
    par_cripto = par_cripto.group(0) if par_cripto else "Desconhecido"
    alavancagem = alavancagem.group(1) if alavancagem else "Desconhecido"
    entrada_min = entrada.group(1) if entrada else "Desconhecido"
    entrada_max = entrada.group(2) if entrada else "Desconhecido"


    # Definir cores
    cor_branca = (255, 255, 255)
    cor_verde = (0, 255, 0)
    cor_vermelha = (255, 0, 0)
    cor_amarela = (255, 204, 0)

    # Posições iniciais
    y_texto = 350
    espacamento = 95

    # Desenhar os elementos na ordem correta
    draw.text((largura // 2 - 300, y_texto), par_cripto, font=fonte_titulo, fill=cor_branca)
    y_texto += espacamento * 2

    draw.text((largura // 2 - 450, y_texto), f"DIRECTION: {direcao}", font=fonte_texto, fill=cor_verde if direcao == "LONG" else cor_vermelha)
    y_texto += espacamento * 1.5

    draw.text((largura // 2 - 450, y_texto), f"LEVERAGE: CROSS {alavancagem}X", font=fonte_texto, fill=cor_amarela)
    y_texto += espacamento * 1.5

    draw.text((largura // 2 - 450, y_texto), f"ENTRY: {entrada_min} - {entrada_max}", font=fonte_texto, fill=cor_branca)
    y_texto += espacamento * 1.5

    draw.text((largura // 2 - 450, y_texto), "TAKE PROFITS:", font=fonte_texto, fill=cor_branca)
    y_texto += espacamento * 1.5
    
    for i, tp in enumerate(take_profits, start=1):
        draw.text((largura // 2 - 450, y_texto), f"TP {i} - {tp}", font=fonte_texto, fill=cor_branca)
        y_texto += espacamento // 1.5

    y_texto += espacamento // 2
    draw.text((largura // 2 - 450, y_texto), f"STOP LOSS: {stop_loss}", font=fonte_texto, fill=cor_vermelha)

    # Salvar a imagem final
    img_fundo.save(nome_arquivo)
    print(f"Imagem salva como {nome_arquivo}")

    return nome_arquivo

# Iniciar o bot
print("Bot rodando...")
client.run_until_disconnected()
