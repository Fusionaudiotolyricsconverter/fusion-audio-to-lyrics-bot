import os
import telebot
import whisper

# 1. Setup
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# 2. AI Model Load karna (Ye ek baar time lega start hone mein)
print("Loading Whisper AI Model...")
model = whisper.load_model("tiny") 
print("Model Loaded!")

# 3. Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 Ricky Bhai! Main ready hoon. Koi bhi Audio/Voice bhejo, main Lyrics nikal dunga!")

# 4. Audio Handling Logic
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    try:
        status_msg = bot.reply_to(message, "🎧 Audio mil gaya! Likh raha hoon (Transcribing)...")
        
        # File Download
        file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Temp Save
        file_name = "temp_audio.ogg"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        # AI Transcription (Magic)
        result = model.transcribe(file_name)
        text = result["text"]

        # Reply with Lyrics
        bot.reply_to(message, f"📝 **Lyrics/Text:**\n\n{text}")
        
        # Cleanup
        os.remove(file_name)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Error aaya: {e}")

# 5. Keep Running
print("Bot Started...")
bot.infinity_polling()

