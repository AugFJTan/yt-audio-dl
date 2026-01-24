from flask import Flask, render_template, request, session, jsonify, copy_current_request_context
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from pathlib import Path
from options import set_user_opts
import yt_dlp
import os
import uuid
import threading
import shutil
import logging
import logging.handlers
import datetime


LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

Path('logs').mkdir(exist_ok=True)

formatter = logging.Formatter(LOG_FORMAT)

handler = logging.handlers.TimedRotatingFileHandler('logs/yt-audio-dl.log', when='midnight', backupCount=7)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)

app = Flask(__name__)
socketio = SocketIO(app)

load_dotenv()
app.secret_key = os.environ.get('secret_key')

session_record = set()

# TODO: Restore client state on page refresh
# TODO: Check for invalid data

@socketio.on('submit')
def submit(url, user_opts):
    downloads = []

    def yt_dlp_log(msg):
        emit('log', msg)

    class WebLogger:
        def debug(self, msg):
            logger.info('%s - yt-dlp - %s', session['id'], msg)
            yt_dlp_log(msg)

        def warning(self, msg):
            logger.warning('%s - yt-dlp - %s', session['id'], msg)
            yt_dlp_log(msg)

        def error(self, msg):
            logger.error('%s - yt-dlp - %s', session['id'], msg)
            yt_dlp_log(msg)

    def filename_hook(d):
        if d['status'] == 'finished':
            download_path = Path(d['filename']).with_suffix('.mp3')
            download = {
                'path': str(download_path.parent),
                'filename': download_path.name
            }
            downloads.append(download)
            logger.info('%s - system - Added %s to download list', session['id'], download_path.name)

    sid = session['id']

    session_dir = f'static/temp/{sid}/'
    Path(session_dir).mkdir(parents=True, exist_ok=True)

    # Default options
    ydl_opts = {
        'outtmpl': {
            'default': session_dir + '%(uploader)s - %(title)s.%(ext)s'
        },
        'windowsfilenames': True,
        'download_archive': session_dir + 'archive.txt',
        'format': 'mp3/bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3'
            }
        ],
        'logger': WebLogger(),
        'color': {
            'stdout': 'no_color',
            'stderr': 'no_color'
        },
        'progress_hooks': [filename_hook]
    }

    set_user_opts(ydl_opts, user_opts)

    try:
        URLS = [url]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(URLS)
    except:
        pass

    emit('list_downloads', downloads)

    if len(downloads) > 0 and sid not in session_record:
        session_record.add(sid)
        # Keep files for 15 minutes
        t = threading.Timer(15 * 60, delete_session_files, [sid])
        t.start()

        delete_files_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
        logger.info('%s - system - Scheduled to delete files at %s', sid, delete_files_time.strftime('%Y-%m-%d %H:%M:%S'))


def delete_session_files(sid):
    session_dir = f'static/temp/{sid}/'
    shutil.rmtree(session_dir, ignore_errors=True)
    session_record.remove(sid)
    logger.info('system - Deleted files from session %s', sid)


@socketio.on('get_session_id_resp')
def client_get_session_id(sid):
    if not sid:
        sid = uuid.uuid4().hex
        logger.info('system - Creating new session %s', sid)
    else:
        logger.info('system - Got existing session %s', sid)
    session['id'] = sid
    emit('set_session_id', sid)


@socketio.on('connect')
def client_connect():
    logger.info('system - Client connected')
    emit('get_session_id')


@socketio.on('disconnect')
def client_disconnect(reason):
    logger.info('%s - system - Client disconnected: %s', session['id'], reason)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
