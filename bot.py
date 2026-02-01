import telebot
import google.generativeai as genai
import os
import time

# 1. SETUP
GEMINI_KEY = "AIzaSyBojK1kFIvvzKbfIGjcgn5i_vAPaDg0_8Y"
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# Using the standard reliable model
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. WELCOME
@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        user_name = message.from_user.first_name
        bot.reply_to(message, f"👋 **Hello {user_name}!**\n\nMain hoon **Fusion Lyrics Bot** 🤖\nSong bhejo, main Lyrics likh dunga!\n\n🚀 *Powered by Fusion Clouds*", parse_mode="Markdown")
    except:
        bot.reply_to(message, "Fusion Bot Ready! Send Audio.")

# 3. MAIN LOGIC
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    try:
        status_msg = bot.reply_to(message, "🎧 **Sun raha hoon...** (Processing...) ⏳")

        # File Download
        file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save
        file_path = f"user_{message.chat.id}.mp3"
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        # Gemini Upload
        audio_file = genai.upload_file(path=file_path)
        
        # Wait for Ready State
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)

        # Generate
        response = model.generate_content([
            "Listen to this audio. Output ONLY the lyrics line by line. Do not write extra text.",
            audio_file
        ])
        
        # Reply with Branding
        final_reply = (
            f"🎶 **LYRICS GENERATED:**\n\n"
            f"{response.text[:3500]}\n\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"🚀 **Fusion Clouds:**\n"
            f"📺 [Subscribe Channel](https://youtube.com/@fusionclouds)\n"
            f"💼 [Hire Me](https://www.fiverr.com/s/gDpmW3A)"
        )
        bot.reply_to(message, final_reply, parse_mode="Markdown")

        # Clean
        os.remove(file_path)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

bot.infinity_polling()
