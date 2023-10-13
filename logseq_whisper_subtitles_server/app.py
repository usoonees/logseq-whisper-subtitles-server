from flask import Flask, request, jsonify
from services import download_youtube, transcribe_audio, extract_audio_from_local_video
import re
import os
import traceback

app = Flask(__name__)


@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        text = request.form['text'].strip()
        min_length = request.form.get('min_length', '')
        segment_symbols = request.form.get('segment_symbols', '')
        model_size = request.form.get('model_size', '')
        graph_path = request.form.get('graph_path', '')

        source = None
        audio_path = None
        youtube_pattern = r"https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+"
        youtube_match = re.search(youtube_pattern, text)
        if youtube_match:
            youtube_url = youtube_match.group()
            audio_path = download_youtube(youtube_url)
            source = "youtube"

        local_video_pattern = r'!\[.*?\]\((.*?)\)'
        local_video_match = re.search(local_video_pattern, text)
        if local_video_match:
            source = "local"
            video_path = local_video_match.group(1)
            if video_path.startswith("../"):
                video_path = os.path.join(graph_path, video_path[3:])

            audio_path = extract_audio_from_local_video(video_path)
            print(f"Extracted file path: {video_path}")

        if source is None:
            return jsonify({
                "source": "",
                "segments": [],
                "error": "not supported source yet"
            })

        return jsonify(
            {
                "error": "",
                "source": source,  # support local etc.
                "segments": transcribe_audio(audio_path, min_length, segment_symbols, model_size)
            })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "logseq-whisper-subtitle-server error: " + str(e),
            "source": "",
            "segments": []
        })


if __name__ == '__main__':
    app.run(debug=True, port=5014)
