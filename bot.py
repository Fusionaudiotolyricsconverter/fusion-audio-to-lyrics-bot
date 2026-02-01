import telebot
import google.generativeai as genai
import os
import time

# 1. SETUP (Railway Variables)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

# Connect to Telegram & Google
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. WELCOME MESSAGE (Professional Style)
@bot.message_handler(commands=['start'])
def welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 **Hello {user_name}!**\n\n"
        f"main hoon **Fusion Lyrics Bot** 🤖\n"
        f"Mujhe koi bhi Song 🎵 ya Voice Note 🎤 bhejo, main turant Lyrics likh kar dunga.\n\n"
        f"🚀 *Powered by Fusion Clouds*"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# 3. MAIN LOGIC (Gemini AI)
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    try:
        # User ko batao kaam shuru hai
        status_msg = bot.reply_to(message, "🎧 **Sun raha hoon...** (Processing Beats & Vocals) ⏳")

        # 1. Download File
        file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # 2. Save Temporarily
        file_path = f"user_{message.chat.id}.mp3"
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        # 3. Send to Google Gemini
        # Upload
        audio_file = genai.upload_file(path=file_path)
        
        # Wait for Google to process audio
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)

        # Generate Lyrics
        prompt = "Listen to this audio. Extract the lyrics exactly line by line. Ignore instrumental parts. Output ONLY the lyrics."
        response = model.generate_content([prompt, audio_file])
        
        # 4. Final Formatting (Branding Added)
        lyrics_text = response.text
        if len(lyrics_text) > 4000:
            lyrics_text = lyrics_text[:4000] + "...(Lyrics too long)"

        final_reply = (
            f"🎶 **LYRICS GENERATED:**\n\n"
            f"{lyrics_text}\n\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"🔥 **Want to make a bot like this?**\n"
            f"Contact: @FusionClouds | Fiverr: lyricsworld9949"
        )

        # Send Reply
        bot.reply_to(message, final_reply)

        # Cleanup
        os.remove(file_path)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Oops! Kuch gadbad hui.\nError: {e}")

# Keep Running
bot.infinity_polling()
