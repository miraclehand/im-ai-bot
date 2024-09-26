"""
import aiohttp
import threading
import atexit
import queue
import uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from confluent_kafka import Producer
from confluent_kafka import Consumer, KafkaException, KafkaError

producer = None
consumer = None
message_queue = queue.Queue()
message = None
res_message = None


async def forward_message2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    message = await update.message.reply_text("Processing...")
    print(user_message, flush=True)

    reply_text = ""
    flag = 0
    async for chunk in stream_to_ollama_agent(user_message):
        if chunk:
            print(chunk, end='', flush=True)
            if chunk == ' ':
                flag = 1
                continue
            if chunk == '\n':
                flag = 2
                continue
            if flag == 1:
                reply_text += " " + chunk
                flag = 0
            elif flag == 2:
                reply_text += "\n" + chunk
                flag = 0
            else:
                reply_text += chunk
            await message.edit_text(reply_text)

async def stream_to_ollama_agent(user_message):
    url = 'http://business-white-paper-service:8080/api/llm-query'
    #url = 'http://127.0.0.1:8080/api/llm-query'

    headers = {"Content-Type": "application/json"}
    data = {"query": user_message}

    async with aiohttp.ClientSession() as session:
        timeout = aiohttp.ClientTimeout(total=6000)  # Adjust the timeout value as needed
        async with session.post(url, json=data, headers=headers, timeout=timeout) as response:
            async for line in response.content:
                if line:
                    chunk = line.decode('utf-8').strip()
                    print(chunk)
                    yield chunk
            # async for chunk in response.content.iter_any():
            #     if chunk:
            #         for char in chunk.decode('utf-8'):
            #             yield char


"""
