import telebot
import requests
import os
from telebot import types
from dotenv import load_dotenv
import sqlite3

conexao = sqlite3.connect('bot_dados.db', check_same_thread=False)
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
               id_telegram INTEGER PRIMARY KEY,
               nome TEXT,
               data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
               )
               ''')
conexao.commit()


load_dotenv()
CHAVE_API = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(CHAVE_API)

@bot.message_handler(commands=["carteira"])
def responder_carteira(mensagem):
    link = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL"
    requisicao = requests.get(link)
    dados = requisicao.json()

    #Pega ovalor
    v_dolar = float(dados["USDBRL"]["bid"])
    v_euro = float(dados["EURBRL"]["bid"])

    exibir_total(mensagem, v_dolar, v_euro)

def exibir_total(msg, d, e):
    soma = (d * 100) + (e * 100)
    bot.reply_to(msg, f"Cotações de hoje: \n Dólar: R${d:.2f}\nEuro R${e:.2f}\n\nSe você tivesse R$100 de cada, teria R$ {soma:.2f}!")

@bot.message_handler(commands=["admin"])
def ver_estatisticas(mensagem):
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]
    bot.reply_to(mensagem, f"Vitor, temos um total de {total} usuario(s) registrados! ")


#1 Decorator que responde apo comando /start ou /ajuda
@bot.message_handler(commands=["start","ajuda"])
def responder_inicio(mensagem):
    # 1. Primeiro pega o nome do cliente
    nome_usuario = mensagem.from_user.first_name
    id_usuario = mensagem.from_user.id
    cursor.execute("INSERT OR IGNORE INTO usuarios (id_telegram, nome) VALUES (?, ?)",
                    (id_usuario, nome_usuario))
    conexao.commit()
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Dólar')
    itembtn2 = types.KeyboardButton('Euro')
    markup.add(itembtn1, itembtn2)
    bot.send_message(mensagem.chat.id, "Escolha uma moeda para ver a cotação:", reply_markup=markup)

# 2. Decorator que filtra mensagens específicos
@bot.message_handler(commands=["vaga"])
def responder_vaga(mensagem):
    bot.send_message(mensagem.chat.id, "Essa vaga de Python parece incrível! Estou estudando para aplicar nela.")

@bot.message_handler(func=lambda message:True)
def responder_geral(mensagem):
    texto_usuario = mensagem.text.lower()

    if ("dólar" in texto_usuario or "dolar" in texto_usuario):
        link = "https://economia.awesomeapi.com.br/last/USD-BRL"
        requisicao = requests.get(link)
        dados = requisicao.json()
        #Pegando o valor e transformando em número (float)
        valor_dolar = float(dados["USDBRL"]["bid"])

       
        bot.reply_to(mensagem, f"O Dólar está custando R$ {valor_dolar:.2f} agora!")
    elif "euro" in texto_usuario:
        link = "https://economia.awesomeapi.com.br/last/EUR-BRL"
        requisicao = requests.get(link)
        dados = requisicao.json()
        valor_euro = float(dados["EURBRL"]["bid"])
        bot.reply_to(mensagem, f"O Euro está R$ {valor_euro:.2f}")
    else:
        bot.reply_to(mensagem,"Não entendi")

# Mantém o bot rodando e verificcando se chegaram novas mensagens
print("Bot online... Pressione Ctrl+C para parar.")
bot.polling()