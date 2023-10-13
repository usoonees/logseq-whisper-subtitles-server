from pytube import YouTube
from datetime import timedelta
import whisper

SEGMENT_SYMBOLS = ['.', '?', '!']
MIN_LENGTH = 0  # set to 0 to disable merging Segments
MODEL_NAME = "base"


def download_youtube(video_url):
    video_url = 'https://www.youtube.com/watch?v=example'
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(filename='output_audio', output_path='.', file_extension='mp3')


def transcribe_audio(path):
    model = whisper.load_model(MODEL_NAME)
    print("Whisper model loaded. 🎧")
    transcribe = model.transcribe(audio=path)
    segments = transcribe['segments']

    previous_segment = None
    previous_start_time = None
    for segment in segments:
        startTime = str(0) + str(timedelta(seconds=int(segment['start']))) + ',000'
        endTime = str(0) + str(timedelta(seconds=int(segment['end']))) + ',000'
        text = segment['text'].strip()
        segmentId = segment['id'] + 1

        # Check if the previous segment needs to be merged
        if previous_segment and (previous_segment[-1] not in SEGMENT_SYMBOLS or len(previous_segment) < MIN_LENGTH):
            previous_segment = f"{previous_segment} {text}"
            endTime = str(0) + str(timedelta(seconds=int(segment['end']))) + ',000'
        else:
            # If this is not the first iteration, print the previous segment
            if previous_segment:
                merged_segment = f"{segmentId-1}\n{previous_start_time} --> {endTime}\n{previous_segment}\n\n"
                print(merged_segment)

            # Set the new previous segment
            previous_segment = text
            previous_start_time = startTime

    # Don't forget the last segment
    if previous_segment:
        last_segment = f"{segmentId}\n{previous_start_time} --> {endTime}\n{previous_segment}\n\n"
        print(last_segment)


transcribe_audio("audio_english.mp3")
