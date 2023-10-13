from pytube import YouTube
from datetime import timedelta
import whisper
import uuid

SEGMENT_SYMBOLS = ['.', '?', '!']
MIN_LENGTH = 0  # set to 0 to disable merging Segments
MODEL_NAME = "base"
print("Loading whisper model...")
model = whisper.load_model(MODEL_NAME)
print("Loading whisper model done.")


def download_youtube(video_url):
    video_url = 'https://www.youtube.com/watch?v=example'
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    vid = uuid.uuid4.hex
    audio_name = f'output_audio_{vid}.mp3'

    audio_stream.download(filename=audio_name, output_path='.')
    return audio_name


def transcribe_audio(path):
    transcribe = model.transcribe(audio=path)
    segments = transcribe['segments']

    previous_segment = None
    previous_start_time = None
    previous_start_time_format = None
    res = []
    for segment in segments:
        start_time = int(segment['start'])
        start_time_format = str(0) + str(timedelta(seconds=int(segment['start'])))
        end_time_format = str(0) + str(timedelta(seconds=int(segment['end'])))
        text = segment['text'].strip()

        # Check if the previous segment needs to be merged
        if previous_segment and (previous_segment[-1] not in SEGMENT_SYMBOLS or len(previous_segment) < MIN_LENGTH):
            previous_segment = f"{previous_segment} {text}"
            end_time_format = str(0) + str(timedelta(seconds=int(segment['end'])))
        else:
            # If this is not the first iteration, print the previous segment
            if previous_segment:
                merged_segment = f"{previous_start_time_format} --> {end_time_format}\n{previous_segment}\n\n"
                print(merged_segment)
                res.append({
                    "startTime": previous_start_time,
                    "segment": previous_segment
                })

            # Set the new previous segment
            previous_segment = text
            previous_start_time_format = start_time_format
            previous_start_time = start_time


    # Don't forget the last segment
    if previous_segment:
        last_segment = f"{previous_start_time_format} --> {end_time_format}\n{previous_segment}\n\n"
        print(last_segment)
        res.append({
            "startTime": previous_start_time,
            "segment": previous_segment
        })

    return res


if __name__ == "__main__":
    res = transcribe_audio("audio_english.mp3")
    print(res)
