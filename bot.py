import telebot
import google.generativeai as genai
import os
import time

# 1. Setup Keys (Railway se lega)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# 2. Model Setup (Gemini 1.5 Flash - Best for Audio)
model = genai.GenerativeModel('gemini-1.5-flash')

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🔥 Fusion Ultra Bot Ready!\nKoi bhi Song 🎵 ya Audio 🎤 bhejo, main lyrics nikal dunga.")

@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    try:
        status = bot.reply_to(message, "🧠 Gaana sun raha hoon (Analyzing with Gemini)...")

        # 1. Download File
        file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # 2. Save Temporarily
        file_path = "song.mp3"
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        # 3. Send to Gemini
        # Upload file
        audio_file = genai.upload_file(path=file_path)
        
        # Wait for processing (Important for Google)
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)

        # Ask for Lyrics
        response = model.generate_content([
            "Listen to this audio. Transcribe the lyrics exactly line by line. Do not describe the music, just give me the text.",
            audio_file
        ])
        
        # 4. Reply
        bot.reply_to(message, f"📝 **Lyrics:**\n\n{response.text}")

        # Cleanup
        os.remove(file_path)
        bot.delete_message(message.chat.id, status.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

bot.infinity_polling()
