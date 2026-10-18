import os
import threading
from flask import Flask
import requests
import telebot
import yt_dlp

# --- TRICK PER TENERE APERTA UNA PORTA SU RENDER ---
app = Flask(__name__)


@app.route("/")
def home():
  return "Il bot è online e attivo!"


def run_web():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


# Avvia il server web fittizio in background
t = threading.Thread(target=run_web)
t.start()
# ---------------------------------------------------

TOKEN = "8716740121:AAFTOJ-iM_n3yBdn97y2m7dHysxlbu3Aojg"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["spotify"])
def handle_spotify(message):
  query = message.text.replace("/spotify", "").strip()
  if not query:
    bot.reply_to(
        message,
        "❌ **Errore:** Scrivi il brano! Es: `/spotify 22simba non siamo voi`",
        parse_mode="Markdown",
    )
    return

  status_msg = bot.reply_to(
      message, f"🔎 Cerco e scarico: *{query}*...", parse_mode="Markdown"
  )
  filename = f"audio_{message.chat.id}.mp3"

  ydl_opts = {
      "format": "bestaudio/best",
      "default_search": "ytsearch1:",
      "outtmpl": filename,
      "quiet": True,
      "postprocessors": [
          {
              "key": "FFmpegExtractAudio",
              "preferredcodec": "mp3",
              "preferredquality": "192",
          }
      ],
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([query])

    with open(filename, "rb") as audio_file:
      bot.send_voice(
          message.chat.id, audio_file, caption=f"🎧 *{query}*", parse_mode="Markdown"
      )

    bot.delete_message(message.chat.id, status_msg.message_id)
  except Exception as e:
    bot.edit_message_text(
        f"❌ Errore: {str(e)}", message.chat.id, status_msg.message_id
    )
  finally:
    if os.path.exists(filename):
      os.remove(filename)


@bot.message_handler(commands=["image"])
def handle_image(message):
  prompt = message.text.replace("/image", "").strip()
  if not prompt:
    bot.reply_to(
        message,
        (
            "❌ **Errore:** Inserisci una descrizione! Es: `/image gatto"
            " astronauta`"
        ),
        parse_mode="Markdown",
    )
    return

  status_msg = bot.reply_to(
      message, f"🎨 Genero l'immagine per: *{prompt}*...", parse_mode="Markdown"
  )
  try:
    prompt_formatted = prompt.replace(" ", "%20")
    image_url = f"https://image.pollinations.ai/prompt/{prompt_formatted}"
    bot.send_photo(
        message.chat.id,
        photo=image_url,
        caption=f"🖼 *{prompt}*",
        parse_mode="Markdown",
    )
    bot.delete_message(message.chat.id, status_msg.message_id)
  except Exception as e:
    bot.edit_message_text(
        f"❌ Errore: {str(e)}", message.chat.id, status_msg.message_id
    )


print("🤖 Bot in ascolto...")
bot.infinity_polling()
