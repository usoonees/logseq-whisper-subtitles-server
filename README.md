## Logseq whisper subtitles

### Overview
logseq-whisper-subtitles-server is a local web server designed to run the whisper service. Its primary role is to extract voice from videos and convert that voice into text. This server is intended to work in conjunction with the [logseq-plugin-whisper-subtitles](https://github.com/usoonees/logseq-plugin-whisper-subtitles) Logseq plugin.

### Prerequisites

Before setting up the server, ensure you have the following dependencies installed:

- **Python:** The server requires Python to run.
- **ffmpeg:** Essential for using the whisper service.

### Installation

1. **Clone the repository** to your local machine:
```bash
git clone https://github.com/usoonees/logseq-whisper-subtitles-server.git
cd logseq-whisper-subtitles-server
```

2. **Install the required Python packages**:
```bash
pip install git+https://github.com/openai/whisper.git 
pip3 install flask pytube
```

### Usage

To start the server, you have two options:

1. **Using the provided bash script**:
```bash
bash run.sh
```

2. **Manually starting the server**:
```bash
cd logseq_whisper_subtitles_server
python3 app.py
```

Ensure the server is running when you use the `logseq-plugin-whisper-subtitles` plugin in Logseq.

### Test
```bash
cd logseq_whisper_subtitles_server
python services.py
```
Output
```
Loading base whisper model...
Loading base whisper model done.
/Users/usoon/miniforge3/envs/test/lib/python3.9/site-packages/whisper/transcribe.py:114: UserWarning: FP16 is not supported on CPU; using FP32 instead
  warnings.warn("FP16 is not supported on CPU; using FP32 instead")
00:00:00 --> 00:00:11
When you hear the term artificial intelligence, what comes to mind?


00:00:09 --> 00:00:13
Superpowered robots?


00:00:11 --> 00:00:18
Hyperintelligent devices?


00:00:13 --> 00:00:29
Science fiction has familiarized the world with the concept, but outside of Hollywood, what is artificial intelligence and what can AI actually do?
....
```

### Related Repository

- [logseq-plugin-whisper-subtitles](#github-link-for-logseq-plugin-whisper-subtitles) - The Logseq plugin that interfaces with this server to extract subtitles and timestamp from videos.
- [whisper](https://github.com/openai/whisper) - The AI model used to extract voice from audio.