from flask import Flask, request, jsonify
from services import download_youtube, transcribe_audio

app = Flask(__name__)


@app.route('/transcribe', methods=['POST'])
def transcribe():
    text = request.form['text'].strip()
    audio_name = download_youtube(text)
    return jsonify(transcribe_audio(audio_name))


if __name__ == '__main__':
    app.run(debug=True)
