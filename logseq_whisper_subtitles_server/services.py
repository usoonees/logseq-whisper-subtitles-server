import uuid
import whisper
from datetime import timedelta
import yt_dlp
import os
import subprocess


def convert_aac_to_mp4(aac_path):
    """
    Convert AAC audio file to MP4 format using ffmpeg

    Args:
        aac_path (str): Path to the input AAC file

    Returns:
        str: Path to the converted MP4 file
    """
    if not os.path.exists(aac_path):
        raise FileNotFoundError(f"AAC file not found: {aac_path}")

    # Create output path by changing extension to .mp4
    output_path = os.path.splitext(aac_path)[0] + ".mp4"

    try:
        # Use ffmpeg to convert AAC to MP4
        command = [
            "ffmpeg",
            "-i",
            aac_path,  # Input file
            "-c:a",
            "copy",  # Copy audio stream without re-encoding
            "-y",  # Overwrite output file if it exists
            output_path,  # Output file
        ]

        # Run the ffmpeg command
        subprocess.run(command, check=True, capture_output=True)

        if not os.path.exists(output_path):
            raise Exception("Conversion failed: Output file not created")

        return output_path

    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg conversion failed: {e.stderr.decode()}")
    except Exception as e:
        raise Exception(f"Error converting AAC to MP4: {str(e)}")


# import re

EN_SEGMENT_SYMBOLS = [".", "?", "!"]
PUNCTUATION = ["，", "。", "？", "！"]
DEFAULT_MIN_LENGTH = 100  # set to 0 to disable merging Segments
DEFAULT_MODEL_SIZE = "base"

print("Loading base whisper model...")
models = {DEFAULT_MODEL_SIZE: whisper.load_model(DEFAULT_MODEL_SIZE)}
print("Loading base whisper model done.")


def is_audio_file(filename):
    audio_extensions = [".mp3", ".wav", ".aac",
                        ".ogg", ".flac", ".m4a", ".wma"]
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower() in audio_extensions


def extract_audio_from_local_video(video_path):
    audio_output_path = os.path.join(
        "local", f"local_audio_{uuid.uuid4().hex}.mp3")
    if not os.path.exists("local"):
        os.makedirs("local")
    command = [
        "ffmpeg",
        "-i",
        video_path,  # Input video file path
        "-q:a",
        "0",  # Quality of audio (0 means best)
        "-map",
        "a",  # Extract audio stream
        "-vn",  # No video output
        audio_output_path,  # Output audio file path
    ]
    try:
        print("Converting local video to audio ...")
        subprocess.run(command)
        print("Converting local video to audio done.")
    except subprocess.CalledProcessError as e:
        print("Converting local video to audio failed.")
        raise RuntimeError(
            f"Failed to convert local video to audio: {e.stderr.decode()}"
        ) from e

    return audio_output_path


def download_youtube(video_url):
    print(f"Downloading the video: {video_url} into audio ...")
    vid = uuid.uuid4().hex
    if not os.path.exists("youtube"):
        os.makedirs("youtube")
    audio_name = os.path.join("youtube", f"youtube_audio_{vid}.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": audio_name,
        "keepvideo": True,  # 保留原始下载的文件
        "postprocessor_args": [
            "-ar",
            "16000",  # 设置音频采样率为16kHz，与原始代码保持一致
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Downloading the video: {video_url} into audio done.")

        # 检查文件是否存在，如果不存在，尝试其他可能的文件名
        if not os.path.exists(audio_name):
            possible_name = audio_name + ".mp3"
            if os.path.exists(possible_name):
                os.rename(possible_name, audio_name)
            else:
                raise FileNotFoundError(
                    f"Could not find the downloaded audio file: {audio_name}"
                )

        return audio_name
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        raise


def replace_punctuation(text):
    text = (
        text.replace(",", "，").replace(
            ".", "。").replace("?", "？").replace("!", "！")
    )
    return text


def transcribe_audio(
    audio_path,
    min_length=DEFAULT_MIN_LENGTH,
    model_size=DEFAULT_MODEL_SIZE,
    zh_type="zh-cn",
):
    if not min_length:
        min_length = DEFAULT_MIN_LENGTH

    if not model_size:
        model_size = DEFAULT_MODEL_SIZE

    if model_size not in models:
        print(f"Loading {model_size} whisper model...")
        models[model_size] = whisper.load_model(model_size)

    model = models[model_size]

    print("Using model: ", model_size)

    if zh_type.strip() == "zh-cn":
        print("Transcribing Chinese simplified audio ...")
        transcribe = model.transcribe(
            audio=audio_path,
            verbose=True,
            initial_prompt="对于普通话句子，以中文简体输出",
        )  # 避免繁体输出
    else:
        transcribe = model.transcribe(audio=audio_path, verbose=True)

    segments = transcribe["segments"]
    detect_language = transcribe.get("language", "")
    print("detected language: ", detect_language)

    previous_segment = None
    previous_start_time = None
    previous_start_time_format = None
    previous_connect_space = " "
    res = []
    for segment in segments:
        start_time = int(segment["start"])
        start_time_format = str(
            0) + str(timedelta(seconds=int(segment["start"])))
        end_time_format = str(0) + str(timedelta(seconds=int(segment["end"])))
        text = segment["text"].strip()
        if not text:  # Skip empty segments
            continue

        cur_connect_space = previous_connect_space
        if detect_language in ["zh", "ja"]:
            text = replace_punctuation(text)
            if text[-1] in PUNCTUATION:
                previous_connect_space = ""
            else:
                previous_connect_space = "，"

        # Check if the previous segment needs to be merged
        is_segment_symbol = text[-1] in EN_SEGMENT_SYMBOLS if text else True

        if detect_language != "en":
            is_segment_symbol = True

        if previous_segment and (
            not is_segment_symbol or len(previous_segment) < int(min_length)
        ):
            previous_segment = f"{previous_segment}{cur_connect_space}{text}"
            end_time_format = str(
                0) + str(timedelta(seconds=int(segment["end"])))
        else:
            # If this is not the first iteration, print the previous segment
            if previous_segment:
                merged_segment = f"{
                    previous_start_time_format} --> {end_time_format}\n{previous_segment}\n\n"
                print(merged_segment)
                res.append(
                    {"startTime": previous_start_time, "segment": previous_segment}
                )

            # Set the new previous segment
            previous_segment = text
            previous_start_time_format = start_time_format
            previous_start_time = start_time

    if previous_segment:
        last_segment = f"{
            previous_start_time_format} --> {end_time_format}\n{previous_segment}\n\n"
        print(last_segment)
        res.append({"startTime": previous_start_time,
                   "segment": previous_segment})

    return res


if __name__ == "__main__":
    print("=== English audio test")
    res_en = transcribe_audio("audio_english.mp3")
    print(res_en)

    print("=== Chinese audio Test")
    res_cn = transcribe_audio("audio_chinese.mp3")
    print(res_cn)
