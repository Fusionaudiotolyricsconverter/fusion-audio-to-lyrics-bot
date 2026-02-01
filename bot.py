
import os
import telebot

# Railway se Token uthana
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

# Start command ka reply
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 Ricky Bhai! Bot Online hai aur Code sahi chal raha hai! 🚀")

# Audio message ka reply (Abhi ke liye basic)
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    bot.reply_to(message, "🎤 Audio mil gaya! Whisper AI model load kar raha hoon...")

print("Fusion Clouds Bot Started...")
bot.infinity_polling()
