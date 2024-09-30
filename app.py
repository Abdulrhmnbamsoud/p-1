import os
import pandas as pd
from flask import Flask, request, jsonify, send_file, render_template
import speech_recognition as sr
from gtts import gTTS
import folium

app = Flask(__name__)

# Load traffic data from CSV files
data_files = [
    'traffic_data_1.csv',
    'traffic_data_2.csv',
    'traffic_data_3.csv',
    'traffic_data_4.csv'
]

# Load the data into Pandas dataframes
dataframes = [pd.read_csv(file) for file in data_files]

# Agent 1: Handle voice input (from Arabic to text)
def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say something in Arabic...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language="ar-SA")
            return text
        except sr.UnknownValueError:
            return "لم أتمكن من التعرف على الصوت"
        except sr.RequestError as e:
            return f"حدث خطأ في طلب الخدمة: {str(e)}"

# Agent 2: Respond with Arabic text based on the keyword and open the corresponding file
def agent_response(keyword):
    file_paths = {
        "طريق": 'traffic_data_1.csv',
        "زحمة": 'traffic_data_2.csv',
        "سرعة": 'traffic_data_3.csv',
        "وقت": 'traffic_data_4.csv'
    }
    
    file_path = file_paths.get(keyword)
    
    if file_path:
        try:
            df = pd.read_csv(file_path)
            response_text = f"تم فتح الملف المتعلق بـ {keyword}. عدد السجلات: {len(df)}"
        except FileNotFoundError:
            response_text = f"الملف المرتبط بـ {keyword} غير موجود."
    else:
        response_text = "لا توجد معلومات متاحة حول هذا الموضوع."

    return response_text

# Agent 3: Generate voice response for the Arabic text
def generate_voice_response(text):
    tts = gTTS(text=text, lang='ar')
    voice_file = "response.mp3"
    tts.save(voice_file)
    return voice_file

@app.route('/process_voice', methods=['POST'])
def process_voice():
    data = request.get_json()
    keyword = data.get("keywords", "")

    # Agent 2: Get the response from the agent based on the keyword
    response_text = agent_response(keyword)

    # Agent 3: Generate a voice response
    voice_file = generate_voice_response(response_text)

    return jsonify({
        "transcription": keyword,
        "response_text": response_text,
        "voice_response": f"/get_audio/{voice_file}"
    })

@app.route('/start_voice', methods=['GET'])
def start_voice():
    # Agent 1: Get the speech input and convert to text
    keyword = recognize_speech_from_mic()

    # Agent 2: Get the response from the agent based on the keyword
    response_text = agent_response(keyword)

    # Agent 3: Generate a voice response
    voice_file = generate_voice_response(response_text)

    return jsonify({
        "transcription": keyword,
        "response_text": response_text,
        "voice_response": f"/get_audio/{voice_file}"
    })

@app.route('/get_audio/<filename>', methods=['GET'])
def get_audio(filename):
    return send_file(filename, mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(debug=True)
