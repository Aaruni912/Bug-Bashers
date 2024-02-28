import telebot
from telebot import types
import random
import string
import json

API_TOKEN = '7113329314:AAF3RLHLlTgvA2e61sby9kQPYtOIuVq7Lao'
bot = telebot.TeleBot(API_TOKEN)

passwords_file = 'passwords.json'

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def save_password(site, password):
    try:
        with open(passwords_file, 'r') as file:
            passwords = json.load(file)
    except FileNotFoundError:
        passwords = {}
    except json.JSONDecodeError:
        passwords = {}

    passwords[site] = password

    with open(passwords_file, 'w') as file:
        json.dump(passwords, file, indent=4)

def search_password(site):
    try:
        with open(passwords_file, 'r') as file:
            passwords = json.load(file)
            return passwords.get(site)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Password Generator Bot!\nUse /gen to generate a new password.\nUse /search to search for an existing password.")

@bot.message_handler(commands=['gen'])
def generate(message):
    msg = bot.reply_to(message, "Which app is this password for?")
    bot.register_next_step_handler(msg, process_site_name)

def process_site_name(message):
    site = message.text
    existing_password = search_password(site)
    if existing_password:
        bot.reply_to(message, f"Oops! A password for **{site}** already exists.", parse_mode='Markdown')
    else:
        password = generate_password()
        save_password(site, password)
        markup = types.InlineKeyboardMarkup()
        regen_button = types.InlineKeyboardButton("Regenerate", callback_data=f"regen_{site}")
        markup.add(regen_button)
        bot.reply_to(message, f"**Site**: `{site}`\n**Password**: `{password}`\n\nPassword saved and ready to copy!", reply_markup=markup, parse_mode='Markdown')

import time

@bot.callback_query_handler(func=lambda call: call.data.startswith('regen_'))
def regenerate_password(call):
    site = call.data.split('_')[1]
    password = generate_password()
    save_password(site, password)
    bot.answer_callback_query(call.id, "Password regenerated!")
    markup = types.InlineKeyboardMarkup()
    regen_button = types.InlineKeyboardButton("Regenerate", callback_data=f"regen_{site}")
    markup.add(regen_button)
    # Simplified Markdown formatting without backticks for the site and password
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"*Site*: {site}\n*Password*: {password}\n\nPassword saved and ready to copy!", reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(commands=['search'])
def search(message):
    msg = bot.reply_to(message, "Enter the site name to search for its password.")
    bot.register_next_step_handler(msg, process_search)

def process_search(message):
    site = message.text
    password = search_password(site)
    if password:
        bot.reply_to(message, f"**Site**: `{site}`\n**Password**: `{password}`\n\nReady to copy!", parse_mode='Markdown')
    else:
        bot.reply_to(message, "No password found for this site.", parse_mode='Markdown')


bot.polling()
