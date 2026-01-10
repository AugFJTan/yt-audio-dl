FROM python:3.14-slim-trixie

WORKDIR /app

RUN apt update && \
    apt install -y wget xz-utils unzip && \
    apt clean

RUN pip3 install Turbo-Flask yt-dlp[default] python-dotenv

# Credit: https://github.com/Jeeaaasus/youtube-dl/blob/master/Dockerfile
RUN wget -q 'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz' -O - | tar -xJ -C /tmp/ --one-top-level=ffmpeg && \
    chmod -R a+x /tmp/ffmpeg/* && \
    mv $(find /tmp/ffmpeg/* -name ffmpeg) /usr/local/bin/ && \
    mv $(find /tmp/ffmpeg/* -name ffprobe) /usr/local/bin/ && \
    mv $(find /tmp/ffmpeg/* -name ffplay) /usr/local/bin/ && \
    rm -rf /tmp/*

RUN wget -q "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip" -O /tmp/deno.zip && \
    unzip /tmp/deno.zip -d /tmp/deno/ && \
    chmod -R a+x /tmp/deno/* && \\
    mv $(find /tmp/deno/* -name deno) /usr/local/bin/ && \
    rm -rf /tmp/*

EXPOSE 5000

ENTRYPOINT FLASK_APP=/app/app.py flask run --host=0.0.0.0
