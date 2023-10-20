## logseq-whisper-subtitles-server

Whisper 文字起こし プラグイン(Logseq)用の専用サーバー (ローカルにセットアップ)　[English](README.md) | [日本語](README.ja.md)

### 概要
* このサーバーは、[logseq-plugin-whisper-subtitles](https://github.com/usoonees/logseq-plugin-whisper-subtitles) というLogseq用プラグインと連携して動作することを意図しています。
* PC上のローカルにインストールされたWhisperサービス(処理サーバー)に要求し、そのデータを受信するために設計されたローカルサーバーです。
   > サーバーのセットアップだけでなく、その依存関係のインストールも必要です。

### 依存関係

両方ともインストールしてください。
1. **Python：** サーバーの実行には、Python が必須です。
   > 次のいずれかを参考にしてください。
   1. [Windows版 Python のインストール](https://www.python.jp/install/windows/install.html)
   2. [macOS版 Python のインストール](https://www.python.jp/install/macos/install_python.html)
1. **ffmpeg：** Whisper サービスを動作させるために必須です。
   1. コマンドプロント(ターミナル)などから、次のいずれかのコマンドを実行し、インストールしてください。※[Whisper セットアップ ドキュメント (英語)](https://github.com/openai/whisper#setup)より
    ```
    # MacOS では、 Homebrew (https://brew.sh/) を使います。
    brew install ffmpeg

    # Windows では、Chocolatey (https://chocolatey.org/) 使います。
    choco install ffmpeg
    ```

### セットアップ

> 専用サーバーをセットアップする前に、依存関係がインストールされていることを確認してください。

1. PC上のローカルに、リポジトリをクローンします
   > どこか安全な場所に新しいフォルダを作成し、そのフォルダに対して、次のコマンドを実行します。Windows 11 の場合は、そのフォルダを右クリックして ターミナルを開きます。
   ```bash
   git clone https://github.com/usoonees/logseq-whisper-subtitles-server.git
   cd logseq-whisper-subtitles-server
   ```

1. Python用パッケージをインストールします

   ```bash
   pip install git+https://github.com/openai/whisper.git 
   pip3 install flask pytube openai-whisper
   ```

1. 初回のため、依存関係に問題がないかテスト動作をおこない、Whisper が正しく使える状態かどうか確認します

   ```bash
   cd logseq_whisper_subtitles_server
   python services.py
   ```

1. コマンドプロントなどに表示される結果が、次のような出力であれば、セットアップが成功しています。

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

  1. セットアップが終わったら、次に進み、専用サーバーを起動します。

### 起動方法

専用サーバーを起動するには、2つのオプションがあります：

1. **サーバーを手動で起動する**:
   - セットアップで作成されたフォルダ(**logseq-whisper-subtitles-server**)の中にある **logseq_whisper_subtitles_server** というフォルダに対して、次のコマンドを実行します。
      > とても紛らわしいですが、"logseq-whisper-subtitles-server > logseq_whisper_subtitles_server" というフォルダ構造になっています。その中に、app.pyというPython実行ファイルが格納されています。
   1. "app.py"という専用アプリをpythonに立ち上げます
      ```bash
      python3 app.py
      ```
      > "python3"でエラーがでる場合は、"python"でも大丈夫です。

1. bash スクリプトを使用 (オプション)

   ```bash
   bash run.sh
   ```

Logseq で専用プラグイン(**logseq-plugin-whisper-subtitles**)を使用する場合は、サーバーが実行されていることを確認してください。

### 関連リポジトリ

- [logseq-plugin-whisper-subtitles](https://github.com/usoonees/logseq-plugin-whisper-subtitles) - ローカルのWhisperに要求して、文字起こしをおこない、Logseqにその内容を取り込むまでをサポートするプラグインです。
- [Whisper](https://github.com/openai/whisper) - 音声認識モデルと呼ばれます。動画からその音声を抽出し、さらにテキストを抽出します。