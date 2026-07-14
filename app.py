import os
import speech_recognition as sr
from flask import Flask, request, render_template, send_file
from deep_translator import GoogleTranslator
from gtts import gTTS
from langdetect import detect
from transformers import pipeline

app = Flask(__name__)

LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "ja": "Japanese",
    "ko": "Korean",
    "te": "Telugu",
    "ml": "Malayalam"
}

# AI Summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# AI Sentiment
sentiment = pipeline("sentiment-analysis")


def recognize_voice():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except:
        return ""


@app.route("/", methods=["GET", "POST"])
def home():

    translated_text = None
    original_text = None
    detected_language = None
    summary = None
    emotion = None

    if request.method == "POST":

        target = request.form.get("target")

        # Voice Button
        if request.form.get("voice") == "1":
            original_text = recognize_voice()
        else:
            original_text = request.form.get("text")

        if original_text:

            # Detect Language
            detected_language = detect(original_text)

            # Translate
            translated_text = GoogleTranslator(
                source="auto",
                target=target
            ).translate(original_text)

            # Voice Output
            tts = gTTS(translated_text, lang=target)
            tts.save("translated_voice.mp3")

            # AI Summary
            if len(original_text.split()) > 30:
                summary = summarizer(
                    original_text,
                    max_length=60,
                    min_length=20,
                    do_sample=False
                )[0]["summary_text"]
            else:
                summary = original_text

            # AI Sentiment
            emotion = sentiment(original_text)[0]

    return render_template(
        "index.html",
        languages=LANGUAGES,
        translated_text=translated_text,
        original_text=original_text,
        detected_language=detected_language,
        summary=summary,
        emotion=emotion
    )


@app.route("/audio")
def audio():
    return send_file("translated_voice.mp3", mimetype="audio/mpeg")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
