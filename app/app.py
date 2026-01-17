from flask import Flask, render_template, request, session, jsonify, copy_current_request_context
from turbo_flask import Turbo
from dotenv import load_dotenv
from pathlib import Path
import yt_dlp
import os
import re

app = Flask(__name__)
turbo = Turbo(app)

load_dotenv()
app.secret_key = os.environ.get('secret_key')


@turbo.user_id
def get_user_id():
    with app.app_context():
        return session['id']


@app.context_processor
def inject_log():
    return dict(log='\n'.join(session['log']))


@app.context_processor
def inject_submit_button():
    return dict(disabled_attr=session['disabled_attr'])


@app.context_processor
def inject_downloads():
    return dict(downloads=session['downloads'])


def turbo_update(element):
    with app.app_context():
        turbo.push(turbo.replace(render_template(f'{element}.html'), element),
                   to=session['id'])


# TODO: Check for invalid data
# TODO: Delete mp3 after session end
# TODO: Handle client reconnection
# TODO: Add logging
# TODO: Update GUI, make it mobile-friendly
# TODO: Add Sponsorblock
# TODO: Sanitize filename - may have to change underscore back to space
# TODO: Add download archive check

progress_rgx = re.compile(r"^\[download\]\s+[0-9]+(\.[0-9]+)?% of.*$")

@app.route('/submit', methods=['POST'])
def submit():
    def yt_dlp_log(msg):
        overwrite_progress = False
        if progress_rgx.match(msg):
            if progress_rgx.match(session['log'][-1]):
                session['log'][-1] = msg
                overwrite_progress = True
        if not overwrite_progress:
            session['log'].append(msg)
        turbo_update('log')

    class WebLogger:
        def debug(self, msg):
            yt_dlp_log(msg)

        def warning(self, msg):
            yt_dlp_log(msg)

        def error(self, msg):
            yt_dlp_log(msg)

    def filename_hook(d):
        if d['status'] == 'finished':
            download_path = Path(d['filename']).with_suffix('.mp3')
            download = {
                "path": str(download_path),
                "filename": download_path.name
            }
            session['downloads'].append(download)

    session_dir = f"static/{session['id']}/"
    Path(session_dir).mkdir(exist_ok=True)

    ydl_opts = {
        'outtmpl': session_dir + '%(uploader)s - %(title)s.%(ext)s',
        'format': 'mp3/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'logger': WebLogger(),
        'progress_hooks': [filename_hook]
    }

    session['disabled_attr'] = 'disabled'
    turbo_update('submit_button')

    try:
        URLS = [request.form['yt-url']]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(URLS)
    except:
        pass

    turbo_update('downloads')

    session['disabled_attr'] = ''
    turbo_update('submit_button')

    return jsonify(message='success')


@app.route('/')
def index():
    if 'id' not in session:
        session['id'] = turbo.default_user_id()
        session['log'] = []
        session['disabled_attr'] = ''
        session['downloads'] = []
    return render_template('index.html')
