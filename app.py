#!/usr/bin/env python3
"""
ClipSave - YouTube video downloader web app (server).

Run locally:
    pip install -r requirements.txt
    python app.py

Production:
    gunicorn -w 2 -b 127.0.0.1:5000 app:app
"""
import os
import re
import sys
import json
import time
import shutil
import tempfile
import subprocess
from collections import defaultdict

from flask import Flask, request, jsonify, render_template_string, send_file, abort, after_this_request

app = Flask(__name__)

# ---- inlined front-end (single-file build; no templates/ or static/ folders) ----
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ClipSave — YouTube Video Downloader | Download in HD, 4K & MP3</title>
<meta name="description" content="ClipSave lets you download YouTube videos in HD, Full HD, 4K and MP3. Free, fast, no signup required.">
<style>
:root{
  --bg:#0f1115; --bg2:#161a21; --card:#1c212b; --line:#2a3140;
  --txt:#f2f4f8; --mut:#9aa3b2; --red:#ff2d3f; --red2:#d61f30;
  --radius:14px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:"Segoe UI",Roboto,Arial,sans-serif;line-height:1.6}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.narrow{max-width:760px}
a{color:var(--txt)}

/* nav */
.nav{background:#0b0d11;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}
.nav-in{display:flex;align-items:center;justify-content:space-between;height:60px}
.logo{font-size:22px;font-weight:800;text-decoration:none;letter-spacing:.5px}
.logo-mark{color:var(--red)}
.links a{margin-left:22px;color:var(--mut);text-decoration:none;font-size:15px}
.links a:hover{color:var(--txt)}

/* hero */
.hero{padding:64px 0 40px;text-align:center;background:radial-gradient(700px 340px at 50% -60px,#2a0f14,var(--bg))}
.hero h1{font-size:clamp(30px,5vw,52px);font-weight:800;margin-bottom:12px}
.sub{color:var(--mut);font-size:18px;max-width:640px;margin:0 auto 28px}
.sub strong{color:var(--txt)}
.dl-box{display:flex;gap:10px;max-width:700px;margin:0 auto;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:8px}
.dl-box input{flex:1;background:transparent;border:0;outline:0;color:var(--txt);font-size:16px;padding:12px 14px;min-width:0}
.dl-box button{background:var(--red);border:0;color:#fff;font-size:17px;font-weight:700;padding:12px 34px;border-radius:10px;cursor:pointer;white-space:nowrap}
.dl-box button:hover{background:var(--red2)}
.tiny{color:var(--mut);font-size:13px;margin-top:14px}

/* status + result */
.status{max-width:700px;margin:18px auto 0;padding:12px 16px;border-radius:10px;font-size:15px}
.status.loading{background:#13202e;color:#7fc4ff}
.status.error{background:#2e1418;color:#ff9aa3}
.result{display:flex;gap:18px;max-width:760px;margin:22px auto 0;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;text-align:left}
.r-thumb{width:220px;max-width:40%;border-radius:10px;object-fit:cover;align-self:flex-start}
.r-body{flex:1;min-width:0}
.r-body h3{font-size:17px;margin-bottom:6px;word-break:break-word}
.r-meta{color:var(--mut);font-size:14px;margin-bottom:14px}
.quals{display:flex;flex-wrap:wrap;gap:10px}
.qbtn{display:inline-block;background:#232a38;border:1px solid var(--line);color:var(--txt);text-decoration:none;font-size:14px;font-weight:600;padding:9px 16px;border-radius:9px}
.qbtn:hover{background:var(--red);border-color:var(--red)}

/* ad slots */
.ad-slot{margin:26px auto;min-height:100px;max-width:970px;border:1.5px dashed #3a4358;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#5b6579;font-size:13px;letter-spacing:2px;text-transform:uppercase;background:#12151c}

/* sections */
.section{padding:56px 0}
.section.alt{background:var(--bg2)}
.section h2{text-align:center;font-size:30px;margin-bottom:32px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:24px 20px}
.card .ic{font-size:30px;margin-bottom:10px}
.card h3{font-size:17px;margin-bottom:8px}
.card p{color:var(--mut);font-size:14px}
.step{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:28px 22px;text-align:center}
.step .n{width:44px;height:44px;border-radius:50%;background:var(--red);font-weight:800;font-size:20px;display:flex;align-items:center;justify-content:center;margin:0 auto 14px}
.step h3{margin-bottom:8px}
.step p{color:var(--mut);font-size:14px}

/* faq */
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:10px}
summary{cursor:pointer;font-weight:600;font-size:16px}
details p{color:var(--mut);margin-top:10px;font-size:15px}

/* footer */
footer{border-top:1px solid var(--line);padding:26px 0;background:#0b0d11}
.foot{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;color:var(--mut);font-size:14px}
.foot nav a{margin-left:18px;color:var(--mut);text-decoration:none}
.foot nav a:hover{color:var(--txt)}

@media(max-width:720px){
  .grid4,.grid3{grid-template-columns:1fr}
  .dl-box{flex-direction:column}
  .dl-box button{width:100%}
  .result{flex-direction:column}
  .r-thumb{width:100%;max-width:100%}
  .links{display:none}
}

</style>
</head>
<body>

<header class="nav">
  <div class="wrap nav-in">
    <a class="logo" href="/"><span class="logo-mark">&#9654;</span> ClipSave</a>
    <nav class="links">
      <a href="#how">How it works</a>
      <a href="#faq">FAQ</a>
    </nav>
  </div>
</header>

<main>
  <!-- HERO -->
  <section class="hero">
    <div class="wrap">
      <h1>YouTube Video Downloader</h1>
      <p class="sub">Paste any YouTube link and download it in <strong>HD, Full HD, 4K</strong> or as <strong>MP3</strong>. Free forever, no signup.</p>

      <form id="dl-form" class="dl-box" autocomplete="off">
        <input id="url-input" type="url" placeholder="Paste YouTube link here…  e.g. https://www.youtube.com/watch?v=…" required>
        <button type="submit">Download</button>
      </form>

      <div id="status" class="status" hidden></div>

      <div id="result" class="result" hidden>
        <img id="r-thumb" class="r-thumb" alt="video thumbnail">
        <div class="r-body">
          <h3 id="r-title"></h3>
          <p id="r-meta" class="r-meta"></p>
          <div id="r-quals" class="quals"></div>
        </div>
      </div>

      <p class="tiny">Works with youtube.com, youtu.be and Shorts links.</p>
    </div>
  </section>

  <!-- AD SLOT 1: leaderboard banner under the hero.
       Paste your AdSense / Adsterra / Monetag banner code inside the div below. -->
  <div class="wrap">
    <div class="ad-slot">
      <span>Advertisement</span>
    </div>
  </div>

  <!-- FEATURES -->
  <section class="section">
    <div class="wrap">
      <h2>Why ClipSave?</h2>
      <div class="grid4">
        <div class="card"><div class="ic">&#127916;</div><h3>4K &amp; HD Quality</h3><p>Download in up to 4K Ultra HD, Full HD 1080p or smaller sizes for your phone.</p></div>
        <div class="card"><div class="ic">&#127925;</div><h3>MP3 Audio</h3><p>Grab just the audio from any video as a high-quality MP3 file.</p></div>
        <div class="card"><div class="ic">&#9889;</div><h3>Fast &amp; Free</h3><p>No accounts, no watermarks, no limits. Unlimited downloads, free forever.</p></div>
        <div class="card"><div class="ic">&#128241;</div><h3>Works Everywhere</h3><p>Use it on your phone, tablet or computer — right in the browser.</p></div>
      </div>
    </div>
  </section>

  <!-- HOW -->
  <section id="how" class="section alt">
    <div class="wrap">
      <h2>How it works</h2>
      <div class="grid3">
        <div class="step"><div class="n">1</div><h3>Copy the link</h3><p>Copy the URL of the YouTube video you want to save.</p></div>
        <div class="step"><div class="n">2</div><h3>Paste it above</h3><p>Paste the link into the box and hit Download.</p></div>
        <div class="step"><div class="n">3</div><h3>Pick a quality</h3><p>Choose HD, 4K or MP3 — the file saves straight to your device.</p></div>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section id="faq" class="section">
    <div class="wrap narrow">
      <h2>Frequently asked questions</h2>
      <details><summary>Is ClipSave free?</summary><p>Yes. Every download is free and unlimited, with no account needed.</p></details>
      <details><summary>Which formats can I download?</summary><p>MP4 video from 360p up to 4K (when the video offers it), plus MP3 audio.</p></details>
      <details><summary>Does it work on mobile?</summary><p>Yes — open this site in your phone's browser, paste a link and download.</p></details>
      <details><summary>Do I need to install anything?</summary><p>No. Everything runs in your browser; nothing to install.</p></details>
      <details><summary>Is downloading allowed?</summary><p>Only download videos you own or that are explicitly free to reuse (for example Creative Commons). Downloading copyrighted content without permission may violate YouTube's Terms of Service.</p></details>
    </div>
  </section>

  <!-- AD SLOT 2: second banner before the footer.
       Paste your second ad unit code inside the div below. -->
  <div class="wrap">
    <div class="ad-slot">
      <span>Advertisement</span>
    </div>
  </div>
</main>

<footer>
  <div class="wrap foot">
    <span>&copy; 2026 ClipSave. All rights reserved.</span>
    <nav>
      <a href="/privacy">Privacy</a>
      <a href="/terms">Terms</a>
      <a href="/dmca">DMCA</a>
      <a href="/contact">Contact</a>
    </nav>
  </div>
</footer>

<script>
const form = document.getElementById('dl-form');
const input = document.getElementById('url-input');
const statusBox = document.getElementById('status');
const resultBox = document.getElementById('result');

function showStatus(msg, kind) {
  statusBox.hidden = false;
  statusBox.className = 'status ' + kind;
  statusBox.textContent = msg;
}
function hideStatus() {
  statusBox.hidden = true;
  statusBox.textContent = '';
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const url = input.value.trim();
  if (!url) return;
  resultBox.hidden = true;
  showStatus('Fetching video info…', 'loading');
  try {
    const r = await fetch('/api/info', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url})
    });
    const d = await r.json();
    if (!d.ok) throw new Error(d.error || 'Something went wrong.');
    hideStatus();
    renderResult(d.video);
  } catch (err) {
    showStatus(err.message || 'Network error. Please try again.', 'error');
  }
});

function renderResult(v) {
  document.getElementById('r-thumb').src = v.thumbnail;
  document.getElementById('r-title').textContent = v.title;
  const meta = [v.uploader, v.duration].filter(Boolean).join('  •  ');
  document.getElementById('r-meta').textContent = meta;
  const box = document.getElementById('r-quals');
  box.innerHTML = '';
  v.qualities.forEach(q => {
    const a = document.createElement('a');
    a.className = 'qbtn';
    a.textContent = '⬇ ' + q.label;
    a.href = '/api/download?url=' + encodeURIComponent(v.url) + '&q=' + q.id;
    a.setAttribute('download', '');
    box.appendChild(a);
  });
  resultBox.hidden = false;
  resultBox.scrollIntoView({behavior: 'smooth', block: 'center'});
}

</script>
</body>
</html>

'''

PAGE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} — ClipSave</title>
<style>
:root{
  --bg:#0f1115; --bg2:#161a21; --card:#1c212b; --line:#2a3140;
  --txt:#f2f4f8; --mut:#9aa3b2; --red:#ff2d3f; --red2:#d61f30;
  --radius:14px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:"Segoe UI",Roboto,Arial,sans-serif;line-height:1.6}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.narrow{max-width:760px}
a{color:var(--txt)}

/* nav */
.nav{background:#0b0d11;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}
.nav-in{display:flex;align-items:center;justify-content:space-between;height:60px}
.logo{font-size:22px;font-weight:800;text-decoration:none;letter-spacing:.5px}
.logo-mark{color:var(--red)}
.links a{margin-left:22px;color:var(--mut);text-decoration:none;font-size:15px}
.links a:hover{color:var(--txt)}

/* hero */
.hero{padding:64px 0 40px;text-align:center;background:radial-gradient(700px 340px at 50% -60px,#2a0f14,var(--bg))}
.hero h1{font-size:clamp(30px,5vw,52px);font-weight:800;margin-bottom:12px}
.sub{color:var(--mut);font-size:18px;max-width:640px;margin:0 auto 28px}
.sub strong{color:var(--txt)}
.dl-box{display:flex;gap:10px;max-width:700px;margin:0 auto;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:8px}
.dl-box input{flex:1;background:transparent;border:0;outline:0;color:var(--txt);font-size:16px;padding:12px 14px;min-width:0}
.dl-box button{background:var(--red);border:0;color:#fff;font-size:17px;font-weight:700;padding:12px 34px;border-radius:10px;cursor:pointer;white-space:nowrap}
.dl-box button:hover{background:var(--red2)}
.tiny{color:var(--mut);font-size:13px;margin-top:14px}

/* status + result */
.status{max-width:700px;margin:18px auto 0;padding:12px 16px;border-radius:10px;font-size:15px}
.status.loading{background:#13202e;color:#7fc4ff}
.status.error{background:#2e1418;color:#ff9aa3}
.result{display:flex;gap:18px;max-width:760px;margin:22px auto 0;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;text-align:left}
.r-thumb{width:220px;max-width:40%;border-radius:10px;object-fit:cover;align-self:flex-start}
.r-body{flex:1;min-width:0}
.r-body h3{font-size:17px;margin-bottom:6px;word-break:break-word}
.r-meta{color:var(--mut);font-size:14px;margin-bottom:14px}
.quals{display:flex;flex-wrap:wrap;gap:10px}
.qbtn{display:inline-block;background:#232a38;border:1px solid var(--line);color:var(--txt);text-decoration:none;font-size:14px;font-weight:600;padding:9px 16px;border-radius:9px}
.qbtn:hover{background:var(--red);border-color:var(--red)}

/* ad slots */
.ad-slot{margin:26px auto;min-height:100px;max-width:970px;border:1.5px dashed #3a4358;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#5b6579;font-size:13px;letter-spacing:2px;text-transform:uppercase;background:#12151c}

/* sections */
.section{padding:56px 0}
.section.alt{background:var(--bg2)}
.section h2{text-align:center;font-size:30px;margin-bottom:32px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:24px 20px}
.card .ic{font-size:30px;margin-bottom:10px}
.card h3{font-size:17px;margin-bottom:8px}
.card p{color:var(--mut);font-size:14px}
.step{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:28px 22px;text-align:center}
.step .n{width:44px;height:44px;border-radius:50%;background:var(--red);font-weight:800;font-size:20px;display:flex;align-items:center;justify-content:center;margin:0 auto 14px}
.step h3{margin-bottom:8px}
.step p{color:var(--mut);font-size:14px}

/* faq */
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:10px}
summary{cursor:pointer;font-weight:600;font-size:16px}
details p{color:var(--mut);margin-top:10px;font-size:15px}

/* footer */
footer{border-top:1px solid var(--line);padding:26px 0;background:#0b0d11}
.foot{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;color:var(--mut);font-size:14px}
.foot nav a{margin-left:18px;color:var(--mut);text-decoration:none}
.foot nav a:hover{color:var(--txt)}

@media(max-width:720px){
  .grid4,.grid3{grid-template-columns:1fr}
  .dl-box{flex-direction:column}
  .dl-box button{width:100%}
  .result{flex-direction:column}
  .r-thumb{width:100%;max-width:100%}
  .links{display:none}
}

</style>
</head>
<body>
<header class="nav">
  <div class="wrap nav-in">
    <a class="logo" href="/"><span class="logo-mark">&#9654;</span> ClipSave</a>
  </div>
</header>
<main class="section">
  <div class="wrap narrow">
    <h2>{{ title }}</h2>
    {% for p in paras %}<p>{{ p }}</p>{% endfor %}
    <p><a href="/">&larr; Back to downloader</a></p>
  </div>
</main>
<footer>
  <div class="wrap foot">
    <span>&copy; 2026 ClipSave. All rights reserved.</span>
    <nav>
      <a href="/privacy">Privacy</a>
      <a href="/terms">Terms</a>
      <a href="/dmca">DMCA</a>
      <a href="/contact">Contact</a>
    </nav>
  </div>
</footer>
</body>
</html>

'''



def _find_ytdlp():
    # 1) next to the current python (venv installs put yt-dlp there)
    cand = os.path.join(os.path.dirname(sys.executable), "yt-dlp")
    if os.path.isfile(cand) and os.access(cand, os.X_OK):
        return cand
    # 2) on PATH
    found = shutil.which("yt-dlp")
    if found:
        return found
    # 3) as a python module fallback
    return None


YTDLP_BIN = _find_ytdlp()
COOKIES_FILE = os.environ.get("COOKIES_FILE", "").strip()
DOWNLOAD_TIMEOUT = int(os.environ.get("DOWNLOAD_TIMEOUT", "900"))

# ---------------------------------------------------------------- URL check
YT_PATTERNS = [
    r"^(https?://)?(www\.|m\.)?youtube\.com/watch\?.*v=[\w-]{6,}",
    r"^(https?://)?(www\.|m\.)?youtube\.com/shorts/[\w-]{6,}",
    r"^(https?://)?(www\.|m\.)?youtube\.com/embed/[\w-]{6,}",
    r"^(https?://)?youtu\.be/[\w-]{6,}",
    r"^(https?://)?(www\.|m\.)?music\.youtube\.com/watch\?.*v=[\w-]{6,}",
]


def is_youtube_url(url: str) -> bool:
    url = (url or "").strip()
    return any(re.match(p, url) for p in YT_PATTERNS)


# ---------------------------------------------------------------- qualities
QUALITY_ORDER = ["best", "2160", "1440", "1080", "720", "480", "360", "audio"]

QUALITY_LABELS = {
    "best": "Best Quality",
    "2160": "4K Ultra HD",
    "1440": "2K Quad HD",
    "1080": "Full HD 1080p",
    "720": "HD 720p",
    "480": "480p",
    "360": "360p",
    "audio": "MP3 Audio",
}

QUALITY_SELECTORS = {
    "best": "bv*+ba/b",
    "2160": "bv*[height<=2160]+ba/b[height<=2160]/bv*+ba/b",
    "1440": "bv*[height<=1440]+ba/b[height<=1440]/bv*+ba/b",
    "1080": "bv*[height<=1080]+ba/b[height<=1080]/bv*+ba/b",
    "720": "bv*[height<=720]+ba/b[height<=720]/bv*+ba/b",
    "480": "bv*[height<=480]+ba/b[height<=480]/bv*+ba/b",
    "360": "bv*[height<=360]+ba/b[height<=360]/bv*+ba/b",
    "audio": "ba/b",
}


# ---------------------------------------------------------------- rate limit
_hits = defaultdict(list)
RATE_LIMIT = 40
RATE_WINDOW = 3600  # per hour, per IP


def rate_ok(ip: str) -> bool:
    now = time.time()
    bucket = _hits[ip]
    bucket[:] = [t for t in bucket if now - t < RATE_WINDOW]
    if len(bucket) >= RATE_LIMIT:
        return False
    bucket.append(now)
    return True


# ---------------------------------------------------------------- yt-dlp
def yt_dlp_base_args():
    if YTDLP_BIN:
        args = [YTDLP_BIN]
    else:
        # last resort: run yt_dlp as a module with the current interpreter
        args = [sys.executable, "-m", "yt_dlp"]
    args += ["--no-playlist", "--no-warnings"]
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        args += ["--cookies", COOKIES_FILE]
    return args


def friendly_yt_error(stderr: str) -> str:
    lines = (stderr or "").strip().splitlines()
    last = lines[-1] if lines else ""
    low = last.lower()
    if "sign in to confirm" in low or "not a bot" in low:
        return "YouTube is asking for verification right now. Please try again in a few minutes."
    if "private video" in low:
        return "This video is private and cannot be downloaded."
    if "video unavailable" in low:
        return "This video is unavailable."
    if "unsupported url" in low:
        return "That link is not supported. Paste a normal YouTube video link."
    return (last or "Could not fetch this video.")[-300:]


def fetch_info(url: str) -> dict:
    cmd = yt_dlp_base_args() + [
        "--dump-single-json", "--no-download", "--socket-timeout", "25", url,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=75)
    if p.returncode != 0:
        raise RuntimeError(friendly_yt_error(p.stderr))
    try:
        return json.loads(p.stdout)
    except (json.JSONDecodeError, ValueError):
        raise RuntimeError(friendly_yt_error(p.stderr))


def available_qualities(info: dict):
    heights = {
        f.get("height")
        for f in info.get("formats", [])
        if f.get("height") and f.get("vcodec") not in (None, "none")
    }
    max_h = max(heights) if heights else 0
    out = []
    for q in QUALITY_ORDER:
        if q in ("best", "audio"):
            out.append(q)
        elif max_h >= int(q):
            out.append(q)
    return out


def fmt_duration(secs) -> str:
    try:
        secs = int(secs)
    except (TypeError, ValueError):
        return ""
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ---------------------------------------------------------------- pages
@app.route("/")
def home():
    return render_template_string(INDEX_HTML)


PAGES = {
    "privacy": ("Privacy Policy", [
        "ClipSave does not require an account and does not store your download history.",
        "Pasted video links are used only to fetch the requested video and are never sold or shared.",
        "We may use basic analytics and third-party advertising cookies as described by our ad partners.",
    ]),
    "terms": ("Terms of Service", [
        "ClipSave is a tool for downloading videos you have the right to download.",
        "Only download videos you own, or that are explicitly free to reuse (for example Creative Commons).",
        "Downloading copyrighted content without permission may violate YouTube's Terms of Service and local law.",
        "We may block abusive usage to keep the service fast for everyone.",
    ]),
    "dmca": ("DMCA", [
        "ClipSave respects copyright holders.",
        "If you believe content made available through this service infringes your copyright, contact us with the video URL and proof of ownership.",
        "Valid requests are reviewed and infringing access is removed promptly.",
    ]),
    "contact": ("Contact", [
        "For support, advertising, or takedown requests, email us.",
        "Replace this address with your own support email before launch: support@example.com",
    ]),
}


@app.route("/<page>")
def static_page(page):
    if page not in PAGES:
        abort(404)
    title, paras = PAGES[page]
    return render_template_string(PAGE_HTML, title=title, paras=paras)


# ---------------------------------------------------------------- API
@app.route("/api/info", methods=["POST"])
def api_info():
    ip = request.remote_addr or "unknown"
    if not rate_ok(ip):
        return jsonify(ok=False, error="Too many requests. Please wait a little while."), 429

    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url or not is_youtube_url(url):
        return jsonify(ok=False, error="Please paste a valid YouTube video link."), 400

    try:
        info = fetch_info(url)
    except RuntimeError as e:
        return jsonify(ok=False, error=str(e)), 502
    except Exception:
        return jsonify(ok=False, error="Something went wrong. Please try again."), 500

    thumbs = info.get("thumbnails") or []
    thumb = thumbs[-1].get("url", "") if thumbs else ""

    return jsonify(ok=True, video={
        "id": info.get("id"),
        "title": info.get("title") or "YouTube video",
        "uploader": info.get("uploader") or info.get("channel") or "",
        "duration": fmt_duration(info.get("duration")),
        "thumbnail": thumb,
        "url": url,
        "qualities": [
            {"id": q, "label": QUALITY_LABELS[q]} for q in available_qualities(info)
        ],
    })


@app.route("/api/download")
def api_download():
    url = (request.args.get("url") or "").strip()
    q = request.args.get("q", "best")
    if not url or not is_youtube_url(url):
        abort(400)
    if q not in QUALITY_SELECTORS:
        abort(400)

    tmpdir = tempfile.mkdtemp(prefix="clipsave_")
    try:
        outtmpl = os.path.join(tmpdir, "%(title).60s-%(id)s.%(ext)s")
        cmd = yt_dlp_base_args() + [
            "-f", QUALITY_SELECTORS[q],
            "--outtmpl", outtmpl,
            "--socket-timeout", "30",
            url,
        ]
        if q == "audio":
            cmd += ["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]

        p = subprocess.run(cmd, capture_output=True, text=True, timeout=DOWNLOAD_TIMEOUT)
        files = [
            os.path.join(tmpdir, f) for f in os.listdir(tmpdir)
            if os.path.isfile(os.path.join(tmpdir, f))
        ]
        if p.returncode != 0 or not files:
            raise RuntimeError(friendly_yt_error(p.stderr))

        fpath = max(files, key=os.path.getsize)

        @after_this_request
        def cleanup(response):
            shutil.rmtree(tmpdir, ignore_errors=True)
            return response

        return send_file(fpath, as_attachment=True,
                         download_name=os.path.basename(fpath))
    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


@app.errorhandler(404)
def not_found(_):
    return render_template_string(PAGE_HTML, title="Not found",
                           paras=["The page you are looking for does not exist."]), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
