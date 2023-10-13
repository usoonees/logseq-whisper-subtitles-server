from flask import Flask, request, jsonify
from services import download_youtube, transcribe_audio
import re

app = Flask(__name__)


@app.route('/transcribe', methods=['POST'])
def transcribe():
    text = request.form['text'].strip()
    min_length = request.form.get('min_length', '')
    segment_symbols = request.form.get('segment_symbols', '')
    model_name = request.form.get('model_name', '')

    youtube_pattern = r"https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+"
    youtube_match = re.search(youtube_pattern, text)
    if youtube_match:
        youtube_url = youtube_match.group()
        audio_path = download_youtube(youtube_url)

    return jsonify(transcribe_audio(audio_path, min_length, segment_symbols, model_name))


if __name__ == '__main__':
    app.run(debug=True, port=5014)
