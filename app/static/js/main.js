const socket = io();

socket.on('connect', () => {
  const status = document.getElementById('status');
  status.innerText = '🟢 Connected';
});

socket.on('disconnect', () => {
  const status = document.getElementById('status');
  status.innerText = '🟡 Reconnecting';
})

socket.on('get_session_id', () => {
  let session_id = null;
  if (sessionStorage.getItem('session_id')) {
    session_id = sessionStorage.getItem('session_id');
  }
  socket.emit('get_session_id_resp', session_id);
});

socket.on('set_session_id', (session_id) => {
  sessionStorage.setItem('session_id', session_id);
});

function showHelp() {
  const overlay = document.getElementById('overlay');
  overlay.style.display = 'block';
}

function hideHelp() {
  const overlay = document.getElementById('overlay');
  overlay.style.display = 'none';
}

// Checkbox handling
if (!localStorage.getItem('metadata')) {
  localStorage.setItem('metadata', 'true');  // Metadata is checked by default
}

if (localStorage.getItem('metadata')) {
  const metadata = document.getElementById('metadata');
  metadata.checked = localStorage.getItem('metadata') === 'true';
}

if (localStorage.getItem('thumbnail')) {
  const thumbnail = document.getElementById('thumbnail');
  thumbnail.checked = localStorage.getItem('thumbnail') === 'true';
}

if (localStorage.getItem('sponsorblock')) {
  const sponsorblock = document.getElementById('sponsorblock');
  sponsorblock.checked = localStorage.getItem('sponsorblock') === 'true';
}

function updateMetadataCheckbox(checkbox) {
  localStorage.setItem('metadata', checkbox.checked ? 'true' : 'false');
}

function updateThumbnailCheckbox(checkbox) {
  localStorage.setItem('thumbnail', checkbox.checked ? 'true' : 'false');
}

function updateSponsorBlockCheckbox(checkbox) {
  localStorage.setItem('sponsorblock', checkbox.checked ? 'true' : 'false');
}

const form = document.getElementById('url-submit');
form.addEventListener('submit', (event) => {
  event.preventDefault();

  const textinput = document.getElementById('yt-url');
  const metadata = document.getElementById('metadata');
  const thumbnail = document.getElementById('thumbnail');
  const sponsorblock = document.getElementById('sponsorblock');

  const user_opts = {
    metadata: metadata.checked,
    thumbnail: thumbnail.checked,
    sponsorblock: sponsorblock.checked
  };

  socket.emit('submit', textinput.value, user_opts);
  const submit_button = document.getElementById('submit-button');
  submit_button.disabled = true;
});

socket.on('log', (msg) => {
  const log = document.getElementById('log');
  if (log.value === '') {
    log.value = msg;
    return;
  }

  const progress_rgx = /^\[download\]\s+[0-9]+(\.[0-9]+)?% of.*$/;
  let lines = log.value.split('\n');
  let overwrite_progress = false;
  if (msg.match(progress_rgx)) {
    if (lines[lines.length-1].match(progress_rgx)) {
      lines[lines.length-1] = msg;
      overwrite_progress = true;
    }
  }
  if (!overwrite_progress) {
    lines.push(msg);
  }

  log.value = lines.join('\n');
  log.scrollTop = log.scrollHeight;
});

socket.on('list_downloads', (links) => {
  const submit_button = document.getElementById('submit-button');
  submit_button.disabled = false;

  if (links.length > 0) {
    const downloads_title = document.getElementById('downloads-title');
    downloads_title.innerText = 'Downloads:';
  }

  links.forEach((link) => {
    const download_link = document.createElement('a');
    download_link.setAttribute('href', link.path + '/' + encodeURIComponent(link.filename));
    download_link.setAttribute('download', '');
    download_link.innerText = link.filename;

    const download_item = document.createElement('li');
    download_item.appendChild(download_link);

    const downloads = document.getElementById('downloads');
    downloads.appendChild(download_item);
  });
});
