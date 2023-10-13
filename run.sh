# conda create -n logseq-whisper-subtitles python=3.8
# conda activate logseq-whisper-subtitles
# pip3 install -r requirements.txt
export FLASK_APP=./logseq_whisper_subtitles_server/app.py
# export FLASK_ENV=development # uncomment for development
flask run --host=0.0.0.0 --port=5014
