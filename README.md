# YT Audio DL

A Docker-based web wrapper around [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download audio from any video as MP3!

# Setup

## Create Secret Key

In the `app/` directory, create a `.env` file with your secret key:

```
secret_key=<MY_SUPER_SECRET_KEY>
```

## Docker Installation (Recommended)

1. Build Docker image:

    ```sh
    docker build -t yt-audio-dl:example-tag .
    ```

2. Update `docker-compose.yml`:

    ```yml
    services:
      app:
        container_name: yt-audio-dl-app
        image: yt-audio-dl:example-tag  # Update image name
        environment:
          TZ: "Europe/London"  # Update timezone
    ...
    ```

3. Deploy Docker container:

    ```sh
    docker compose up -d
    ```

## Local Installation

1. Install [ffmpeg](https://www.ffmpeg.org/) and [deno](https://deno.com/).

2. Install Python dependencies:

    ```sh
    pip3 install flask-socketio yt-dlp[default] python-dotenv
    ```

    **Tip:** Install the Python dependencies in a [virtual environment](https://docs.python.org/3/library/venv.html).

3. Run the script:

    ```sh
    cd app/
    python3 app.py
    ```

# Usage

1. In a web browser, open `http://<localhost or IP address>:5000`.

2. Enter a YouTube video or playlist URL and click on the "Submit" button.

3. Click on the links that appear below the log to download the MP3 files.
