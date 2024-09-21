import yt_dlp
from datetime import timedelta
import whisper
import uuid
import os
import subprocess
import torch

EN_SEGMENT_SYMBOLS = ['.', '?', '!']
PUNCTUATION = ['，', '。', '？', '！']
DEFAULT_MIN_LENGTH = 100  # set to 0 to disable merging Segments
DEFAULT_MODEL_SIZE = "base"

# Add diagnostic information
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")

# Check if CUDA is available and force its use if it is
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

print("Loading base whisper model...")
models = {
    DEFAULT_MODEL_SIZE: whisper.load_model(DEFAULT_MODEL_SIZE).to(device)
}
print("Loading base whisper model done.")
print(f"Model device: {next(models[DEFAULT_MODEL_SIZE].parameters()).device}")

def is_audio_file(filename):
    audio_extensions = ['.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a', '.wma']
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower() in audio_extensions

def extract_audio_from_local_video(video_path):
    audio_output_path = os.path.join('local', f'local_audio_{uuid.uuid4().hex}.mp3')
    if not os.path.exists('local'):
        os.makedirs('local')
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
    vid = uuid.uuid4().hex
    if not os.path.exists('youtube'):
        os.makedirs('youtube')
    audio_name = os.path.join('youtube', f'youtube_audio_{vid}.mp3')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': audio_name,
        'keepvideo': True,  # 保留原始下载的文件
        'postprocessor_args': [
            '-ar', '16000'  # 设置音频采样率为16kHz，与原始代码保持一致
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Downloading the video: {video_url} into audio done.")
        
        # 检查文件是否存在，如果不存在，尝试其他可能的文件名
        if not os.path.exists(audio_name):
            possible_name = audio_name + '.mp3'
            if os.path.exists(possible_name):
                os.rename(possible_name, audio_name)
            else:
                raise FileNotFoundError(f"Could not find the downloaded audio file: {audio_name}")
        
        return audio_name
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        raise

def replace_punctuation(text):
    text = text.replace(",", "，").replace(".", "。").replace("?", "？").replace("!", "！")
    return text

def transcribe_audio(audio_path, min_length=DEFAULT_MIN_LENGTH, model_size=DEFAULT_MODEL_SIZE, zh_type='zh-cn'):
    if not min_length:
        min_length = DEFAULT_MIN_LENGTH

    if not model_size:
        model_size = DEFAULT_MODEL_SIZE

    if model_size not in models:
        print(f"Loading {model_size} whisper model...")
        models[model_size] = whisper.load_model(model_size).to(device)

    model = models[model_size]

    print("Using model: ", model_size)
    print(f"Model device: {next(model.parameters()).device}")

    if zh_type.strip() == 'zh-cn':
        print("Transcribing Chinese simplified audio ...")
        transcribe = model.transcribe(audio=audio_path, verbose=True, initial_prompt="对于普通话句子，以中文简体输出", fp16=(device=="cuda"))
    else:
        transcribe = model.transcribe(audio=audio_path, verbose=True, fp16=(device=="cuda"))

    segments = transcribe['segments']
    detect_language = transcribe.get('language', '')型号 = {
    print("detected language: ", detect_language)

    previous_segment = None
    previous_start_time = None
    previous_start_time_format = None
    previous_connect_space = " "
    res = []
    for segment in segments:
        start_time = int(segment['start'])
        start_time_format = str(0) + str(timedelta(seconds=int(segment['start'])))
        end_time_format = str(0) + str(timedelta(seconds=int(segment['end'])))
        text = segment['text'].strip()
        cur_connect_space = previous_connect_space
        if detect_language in ['zh', 'ja']:
            text = replace_punctuation(text)
            if text[-1] in PUNCTUATION:
                previous_connect_space = ""
            else:
                previous_connect_space = "，"

        # Check if the previous segment needs to be merged
        is_segment_symbol = text[-1] in EN_SEGMENT_SYMBOLS

        if detect_language != 'en':
            is_segment_symbol = True

        if previous_segment and (not is_segment_symbol or len(previous_segment) < int(min_length)):
            previous_segment = f"{previous_segment}{cur_connect_space}{text}"
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

    return res

if __name__ == "__main__":
    print("=== English audio test")
    res_en = transcribe_audio("audio_english.mp3")
    print(res_en)

    print("=== Chinese audio Test")
    res_cn = transcribe_audio("audio_chinese.mp3")
    print(res_cn)
