# logseq-whisper-subtitles-server

[English](README.md) | [日本語](README.ja.md)

### Overview
* This server is designed to work in conjunction with the Logseq plugin called [logseq-plugin-whisper-subtitles](https://github.com/usoonees/logseq-plugin-whisper-subtitles).
* It's a local server designed to make requests to the Whisper service (processing server) installed locally on the PC and receive data from it.
   > In addition to setting up the server, it's necessary to install its dependencies.

### Dependencies

Please install both of the following:
1. **Python:** Python is required for running the server.
   1. [Python 3 Installation & Setup Guide](https://realpython.com/installing-python/)
1. **ffmpeg:** This is essential for running the Whisper service.
   1. Execute one of the following commands from the command prompt (terminal) or similar to install it. *[Whisper Setup Documentation](https://github.com/openai/whisper#setup)*
    ```
    # On macOS, use Homebrew (https://brew.sh/).
    brew install ffmpeg

    # On Windows, use Chocolatey (https://chocolatey.org/).
    choco install ffmpeg
    ```

### Setup

> Before setting up the dedicated server, ensure that the dependencies are installed.

1. Clone the repository to the local PC.
   > Create a new folder in a safe location and execute the following commands for that folder. On Windows 11, right-click the folder and open a terminal.
   ```bash
   git clone https://github.com/usoonees/logseq-whisper-subtitles-server.git
   cd logseq-whisper-subtitles-server
   ```

1. Install Python packages.

   ```bash
   pip install git+https://github.com/openai/whisper.git 
   pip3 install flask pytube openai-whisper
   ```

1. For the initial setup, test to ensure there are no issues with the dependencies and that Whisper is functioning correctly.

   ```bash
   cd logseq_whisper_subtitles_server
   python services.py
   ```

1. If the results displayed in the command prompt resemble the following output, the setup is successful:

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

1. Once the setup is complete, proceed to start the dedicated server.

### Starting the Server

To start the dedicated server, 2 options:

1. **Manually start the server**:
   - Execute the following command for the folder named **logseq_whisper_subtitles_server** located inside the folder created during setup (**logseq-whisper-subtitles-server**). 
      > It's a bit confusing, but the folder structure is "logseq-whisper-subtitles-server > logseq_whisper_subtitles_server," and inside it, there's a Python executable called "app.py."
   1. Launch the dedicated app called "app.py" using Python.
      ```bash
      python3 app.py
      ```
      > If encounter an error with "python3," "python" should work as well.

1. Use a bash script (optional)

   ```bash
   bash run.sh
   ```

Make sure that the server is running if intend to use the dedicated plugin (**logseq-plugin-whisper-subtitles**) in Logseq.

### Related Repositories

- [logseq-plugin-whisper-subtitles](https://github.com/usoonees/logseq-plugin-whisper-subtitles) - The Logseq plugin that interfaces with this server to extract subtitles and timestamp from videos.
- [whisper](https://github.com/openai/whisper) - The AI model used to extract voice from audio.
