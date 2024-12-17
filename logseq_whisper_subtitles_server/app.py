from flask import Flask, request, jsonify
from services import (
    download_youtube,
    transcribe_audio,
    extract_audio_from_local_video,
    is_audio_file,
    convert_aac_to_mp4,
)
import re
import os
import traceback

app = Flask(__name__)


@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        text = request.form["text"].strip()
        min_length = request.form.get("min_length", "")
        model_size = request.form.get("model_size", "")
        graph_path = request.form.get("graph_path", "")
        zh_type = request.form.get("zh_type", "zh-cn")

        source = None
        audio_path = None
        youtube_pattern = r"https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+|https://youtu\.be/[a-zA-Z0-9_-]+"
        youtube_match = re.search(youtube_pattern, text)

        local_file_pattern = r"(!\[.*?\]\((.*?)\))|(\{\{renderer :[a-zA-Z]+, (.*?)\}\})|\[\[(.*?)\]\[.*?\]\]"
        local_file_match = re.search(local_file_pattern, text)

        if youtube_match:
            youtube_url = youtube_match.group()
            audio_path = download_youtube(youtube_url)
            source = "youtube"

        elif local_file_match:
            if local_file_match.group(2) is not None:
                local_file_path = local_file_match.group(2)
            elif local_file_match.group(4) is not None:
                local_file_path = local_file_match.group(4)
            elif local_file_match.group(5) is not None:
                local_file_path = local_file_match.group(5)
            else:
                return jsonify(
                    {"source": "", "segments": [],
                        "error": "No local file path found"}
                )

            if local_file_path.startswith("http") or local_file_path.startswith(
                "https"
            ):
                print("This is a URL, not a local file")
                return jsonify(
                    {
                        "source": "",
                        "segments": [],
                        "error": "This is a URL, not a local file",
                    }
                )

            source = "local"
            if local_file_path.startswith("../"):
                local_file_path = os.path.join(graph_path, local_file_path[3:])

            audio_path = local_file_path
            if local_file_path.lower().endswith(".aac"):
                audio_path = convert_aac_to_mp4(local_file_path)
            elif not is_audio_file(local_file_path):
                audio_path = extract_audio_from_local_video(local_file_path)
            print(f"Extracted file path: {local_file_path}")

        else:
            return jsonify(
                {"source": "", "segments": [], "error": "not supported source yet"}
            )

        return jsonify(
            {
                "error": "",
                "source": source,  # support local etc.
                "segments": transcribe_audio(
                    audio_path, min_length, model_size, zh_type
                ),
            }
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify(
            {
                "error": "logseq-whisper-subtitle-server error: " + str(e),
                "source": "",
                "segments": [],
            }
        )


if __name__ == "__main__":
    app.run(debug=True, port=5014)
