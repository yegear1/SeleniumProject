from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from utils import normalize_gpu_name, normalize_price, connect_db, save_csv, normalize_string

import re
import os
import time
import pandas as pd
import logging
from datetime import datetime, timedelta

#logger = logging.getLogger("main")


logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
logger.propagate = False

# Formato dos logs
log_formatter = logging.Formatter('%(levelname)s - %(message)s')

# Manipulador para o terminal (console)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)
console_handler.encoding = 'utf-8'  # Tentar forçar UTF-8 no terminal
logger.addHandler(console_handler)

# Criar a pasta logs se ela não existir
os.makedirs("logs", exist_ok=True)

# Manipulador para o arquivo (salvar logs em um arquivo)
log_filename = f"logs/scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


api_id = "29045797"
api_hash = "159c1efbb8ec3ccc086fe3e16cd5b22b"
phone = "+5586995416560"
group_username = "guigatudo"

client = TelegramClient('session_name', api_id, api_hash)

async def telegram():
    try:
        logger.info("Tentando conectar ao Telegram...")
        await client.start()
        if not await client.is_user_authorized():
            logger.info("Autorização necessária. Enviando código de verificação...")
            await client.send_code_request(phone)
            try:
                await client.sign_in(phone, input('Digite o código recebido: '))
            except SessionPasswordNeededError:
                await client.sign_in(password=input('Digite sua senha: '))

        logger.info("Conexão ao Telegram bem-sucedida!")

        try:
            group = await client.get_entity(group_username)
            logger.info(f"Conectado ao grupo: {group.title}")
        except Exception as e:
            logger.error(f"Erro ao acessar o grupo {group_username}: {e}")
            return
        time.sleep(3)

        gpu_data = []
        message_num = 0

        # Iterar sobre as mensagens do grupo
        async for message in client.iter_messages(group, limit=None):
            if message.text:
                local_date = message.date - timedelta(hours=3)  # Subtrai 3 horas para UTC-3
                current_date = local_date.strftime('%Y-%m-%d')
                logger.info(f"Mensagem número {message_num}")
                message_num += 1

                message_pos = normalize_string(message.text)
                brand_gpu, name_gpu = normalize_gpu_name(message_pos)
                price = normalize_price(message_pos)

                #time.sleep(0.1)

                if brand_gpu is not None:
                    logger.info(f"{brand_gpu} {name_gpu}")
                    logger.info(f"{price}")
                    logger.info(f"{current_date}")
                    gpu_data.append({
                        "Fonte": "Telegram",
                        "Marca": brand_gpu,
                        "Nome": name_gpu,
                        "Preço": price,
                        "Data": current_date,
                    })
                else:
                    continue
            else:
                logger.info("Não contem texto")

        if gpu_data:
            connect_db(gpu_data)
            #save_csv(gpu_data)
            #logger.info(f"Dados salvos em gpu.csv: {len(gpu_data)} registros")
        else:
            logger.info("Nenhum dado de preço encontrado.")

    except Exception as e:
        logger.error(f"Erro ao coletar dados do Telegram: {e}")

# Executar o script
with client:
    logger.info("Iniciando telegram")
    client.loop.run_until_complete(telegram())
