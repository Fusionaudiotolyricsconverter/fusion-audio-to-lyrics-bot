import telebot
import google.generativeai as genai
import os
import time

# 1. SETUP (Direct Key + Corrected Model)
GEMINI_KEY = "AIzaSyBojK1kFIvvzKbfIGjcgn5i_vAPaDg0_8Y"
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Connect
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# FIX: Using the specific version ID to stop the Crash/404 Error
model = genai.GenerativeModel('gemini-1.5-flash-001')

# 2. WELCOME MESSAGE
@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        user_name = message.from_user.first_name
        welcome_text = (
            f"👋 **Hello {user_name}!**\n\n"
            f"Main hoon **Fusion Lyrics Bot** 🤖\n"
            f"Mujhe koi bhi Song 🎵 ya Voice Note 🎤 bhejo, main turant Lyrics likh kar dunga.\n\n"
            f"🚀 *Powered by Fusion Clouds*"
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "Hello! I am ready.")

# 3. MAIN LOGIC
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    try:
        status_msg = bot.reply_to(message, "🎧 **Sun raha hoon...** (Processing Beats & Vocals) ⏳")

        # Download File
        file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save Temporarily
        file_path = f"user_{message.chat.id}.mp3"
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        # Gemini Process
        audio_file = genai.upload_file(path=file_path)
        
        # Wait for processing
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)

        # Generate Lyrics
        prompt = "Listen to this audio. Extract the lyrics exactly line by line. Ignore instrumental parts. Output ONLY the lyrics."
        response = model.generate_content([prompt, audio_file])
        
        # Format Reply
        lyrics_text = response.text
        if len(lyrics_text) > 4000:
            lyrics_text = lyrics_text[:4000] + "...(Lyrics too long)"

        final_reply = (
            f"🎶 **LYRICS GENERATED:**\n\n"
            f"{lyrics_text}\n\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"🚀 **Power up your Channel:**\n"
            f"📺 [Subscribe Fusion Clouds](https://youtube.com/@fusionclouds)\n"
            f"💼 [Hire Me on Fiverr](https://www.fiverr.com/s/gDpmW3A)"
        )
        bot.reply_to(message, final_reply, parse_mode="Markdown")

        # Cleanup
        os.remove(file_path)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        # Error handling taaki user ko pata chale kya hua
        bot.reply_to(message, f"❌ Oops! Error: {e}")

# Start Bot
bot.infinity_polling()
