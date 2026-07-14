import os
from flask import Flask, request, render_template, send_file
from deep_translator import GoogleTranslator
from gtts import gTTS

app = Flask(__name__)

LANGUAGES = {
    "en": "English", "ta": "Tamil", "hi": "Hindi", "fr": "French",
    "es": "Spanish", "de": "German", "ja": "Japanese", "ko": "Korean",
    "te": "Telugu", "ml": "Malayalam"
}

@app.route("/", methods=["GET", "POST"])
def home():
    translated_text = None
    if request.method == "POST":
        text = request.form.get("text")
        target = request.form.get("target")

        # Translate
        translated_text = GoogleTranslator(source="auto", target=target).translate(text)

        # Convert to voice
        tts = gTTS(text=translated_text, lang=target)
        tts.save("translated_voice.mp3")

    return render_template("index.html", languages=LANGUAGES, translated_text=translated_text)

@app.route("/audio")
def audio():
    return send_file("translated_voice.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
