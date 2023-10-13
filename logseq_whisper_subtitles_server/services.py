from pytube import YouTube
from datetime import timedelta
import whisper
import uuid
import os
import subprocess

DEFAULT_SEGMENT_SYMBOLS = ['.', '?', '!']
DEFAULT_MIN_LENGTH = 0  # set to 0 to disable merging Segments
DEFAULT_MODEL_SIZE = "base"

print("Loading base whisper model...")
models = {
    DEFAULT_MODEL_SIZE: whisper.load_model(DEFAULT_MODEL_SIZE)
}
print("Loading base whisper model done.")


def extract_audio_from_local_video(video_path):
    audio_output_path = f'local_audio_{uuid.uuid4().hex}.mp3'
    command = [
        'ffmpeg',
        '-i', video_path,  # Input video file path
        '-q:a', '0',       # Quality of audio (0 means best)
        '-map', 'a',       # Extract audio stream
        '-vn',             # No video output
        audio_output_path  # Output audio file path
    ]
    try:
        print("Converting local video to audio ...")
        subprocess.run(command)
        print("Converting local video to audio done.")
    except subprocess.CalledProcessError as e:
        print("Converting local video to audio failed.")
        raise RuntimeError(f"Failed to convert local video to audio: {e.stderr.decode()}") from e

    return audio_output_path


def download_youtube(video_url):
    print(f"Downloading the video: {video_url} into audio ...")
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    vid = uuid.uuid4().hex
    audio_name = f'youtube_audio_{vid}.mp3'

    audio_stream.download(filename=audio_name, output_path='.')
    print(f"Downloading the video: {video_url} into audio done.")
    return audio_name


def transcribe_audio(audio_path, min_length=DEFAULT_MIN_LENGTH, segment_symbols=DEFAULT_SEGMENT_SYMBOLS, model_size=DEFAULT_MODEL_SIZE):
    if not min_length:
        min_length = DEFAULT_MIN_LENGTH

    if not segment_symbols:
        segment_symbols = DEFAULT_SEGMENT_SYMBOLS

    if not model_size:
        model_size = DEFAULT_MODEL_SIZE

    if model_size not in models:
        models[model_size] = whisper.load_model(model_size)
    model = models[model_size]

    transcribe = model.transcribe(audio=audio_path)
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
        if previous_segment and (previous_segment[-1] not in segment_symbols or len(previous_segment) < int(min_length)):
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

    if previous_segment:
        last_segment = f"{previous_start_time_format} --> {end_time_format}\n{previous_segment}\n\n"
        print(last_segment)
        res.append({
            "startTime": previous_start_time,
            "segment": previous_segment
        })

    os.remove(audio_path)

    return res


if __name__ == "__main__":
    res = transcribe_audio("audio_english.mp3")
    print(res)
