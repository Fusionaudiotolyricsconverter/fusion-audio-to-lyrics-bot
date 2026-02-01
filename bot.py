import telebot
import speech_recognition as sr
import os
from pydub import AudioSegment

# 1. Setup
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
r = sr.Recognizer()

# 2. Start Message
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🔥 Ricky Bhai! Plan B Ready hai. Audio bhejo!")

# 3. Audio Processing (Google Logic)
@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio(message):
    try:
        status = bot.reply_to(message, "🎧 Sun raha hoon (Converting)...")

        # File Download
        file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save OGG
        with open("temp.ogg", "wb") as f:
            f.write(downloaded_file)

        # Convert to WAV (Zaroori hai)
        sound = AudioSegment.from_file("temp.ogg")
        sound.export("temp.wav", format="wav")

        # Transcribe via Google
        with sr.AudioFile("temp.wav") as source:
            audio_data = r.record(source)
            # Hindi/English Mix support
            text = r.recognize_google(audio_data, language="en-IN")

        bot.reply_to(message, f"📝 **Lyrics:**\n\n{text}")

        # Cleanup
        os.remove("temp.ogg")
        os.remove("temp.wav")
        bot.delete_message(message.chat.id, status.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

bot.infinity_polling()
