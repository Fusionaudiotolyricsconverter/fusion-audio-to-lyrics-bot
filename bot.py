import telebot
import google.generativeai as genai
import os
import time

# 1. SETUP (Hardcoded Key)
GEMINI_KEY = "AIzaSyBojK1kFIvvzKbfIGjcgn5i_vAPaDg0_8Y"
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# 2. MODEL SETUP (Standard Flash Model)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. WELCOME
@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        bot.reply_to(message, "👋 **Fusion Bot Ready!**\n\nAudio bhejo, main Lyrics nikal dunga. 🎵", parse_mode="Markdown")
    except:
        pass

# 4. MAIN LOGIC
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    try:
        status_msg = bot.reply_to(message, "🎧 **Sun raha hoon...** (Processing...) ⏳")

        # Download
        file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save
        file_path = f"user_{message.chat.id}.mp3"
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        # Gemini Process
        audio_file = genai.upload_file(path=file_path)
        
        # Wait for Ready
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)

        # Generate
        response = model.generate_content([
            "Listen to this audio. Transcribe lyrics line by line. Output ONLY the lyrics.",
            audio_file
        ])
        
        # Reply
        final_reply = (
            f"🎶 **LYRICS:**\n\n"
            f"{response.text[:3500]}\n\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"🚀 [Subscribe Fusion Clouds](https://youtube.com/@fusionclouds)"
        )
        bot.reply_to(message, final_reply, parse_mode="Markdown")

        # Clean
        os.remove(file_path)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

bot.infinity_polling()
