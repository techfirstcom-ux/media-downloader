import os
import uuid
import tempfile
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import yt_dlp

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Download folder (temp)
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "techfirst_downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Platforms: keep EXACT structure your index.html expects
PLATFORMS = [
    {"name": "YouTube", "value": "youtube"},
    {"name": "Instagram", "value": "instagram"},
    {"name": "Facebook", "value": "facebook"},
    {"name": "Twitter (X)", "value": "twitter"},
]

# ----- Helpers -----
def human_size(bytes_size):
    if not bytes_size or bytes_size <= 0:
        return "?"
    return f"{bytes_size / (1024 * 1024):.2f} MB"

def est_size_from_bitrate_kbps(kbps, duration_sec):
    # yt-dlp's tbr/abr are in KBits/s. Convert to bytes: kbps * 1000 / 8 per second.
    if not kbps or not duration_sec:
        return None
    try:
        return int(kbps * 1000 / 8 * duration_sec)
    except Exception:
        return None

def pick_size(f, duration):
    # Best available size: filesize > filesize_approx > computed from tbr
    fs = f.get("filesize")
    if fs:
        return fs
    fa = f.get("filesize_approx")
    if fa:
        return fa
    tbr = f.get("tbr")  # kbps
    if tbr and duration:
        return est_size_from_bitrate_kbps(float(tbr), duration)
    return None

def fetch_info(url):
    ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# ----- Routes -----
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        mode = request.form.get("mode")
        platform = request.form.get("platform")

        if not url or not mode or not platform:
            flash("Please fill all fields.", "warning")
            return redirect(url_for("index"))

        try:
            info = fetch_info(url)
        except Exception as e:
            flash(f"Error fetching info: {e}", "danger")
            return redirect(url_for("index"))

        duration = info.get("duration") or 0

        # Build audio catalog first (for video size estimates when merging)
        audio_only = []
        for f in info.get("formats", []):
            if f.get("acodec") != "none" and (f.get("vcodec") in (None, "none")):
                abr = f.get("abr")
                if abr is None and f.get("tbr"):
                    abr = float(f["tbr"])
                if abr:
                    size_b = pick_size(f, duration)
                    audio_only.append({
                        "format_id": f.get("format_id"),
                        "abr_kbps": float(abr),
                        "size_b": size_b,
                    })

        # pick best audio for merging size estimates (highest abr)
        best_audio = max(audio_only, key=lambda x: x["abr_kbps"], default=None)

        # Build video options: one per height. Prefer video-only; if not present, use progressive.
        by_height = {}  # height -> dict(format_id, quality, size_b, progressive)
        for f in info.get("formats", []):
            vcodec = f.get("vcodec")
            acodec = f.get("acodec")
            height = f.get("height")

            if not height or vcodec in (None, "none"):
                continue

            is_progressive = acodec not in (None, "none")
            size_b = pick_size(f, duration)

            # Prefer video-only for merging; otherwise progressive.
            current = by_height.get(height)
            candidate = {
                "format_id": f.get("format_id"),
                "quality": f"{height}p",
                "size_b": size_b,
                "is_progressive": is_progressive,
                "tbr": f.get("tbr")
            }

            def rank(entry):
                # Rank: video-only (0) preferred over progressive (1), then larger estimated size
                prog_score = 1 if entry["is_progressive"] else 0
                size_score = entry["size_b"] or 0
                return (prog_score, -size_score)

            if current is None or rank(candidate) < rank(current):
                by_height[height] = candidate

        # Convert to list and compute display size:
        video_formats = []
        for h in sorted(by_height.keys()):
            item = by_height[h]
            total_size_b = item["size_b"]
            if not item["is_progressive"]:
                # add best audio size estimate for display
                if best_audio and best_audio.get("size_b"):
                    total_size_b = (total_size_b or 0) + best_audio["size_b"]
                elif best_audio:
                    # compute audio size from abr if needed
                    est_audio_b = est_size_from_bitrate_kbps(best_audio["abr_kbps"], duration)
                    if est_audio_b:
                        total_size_b = (total_size_b or 0) + est_audio_b

            video_formats.append({
                "format_id": item["format_id"],
                "quality": item["quality"],
                "size_mb": human_size(total_size_b),
            })

        # Audio display list (unique bitrates, highest first)
        audio_formats = []
        seen_abr = set()
        for a in sorted(audio_only, key=lambda x: x["abr_kbps"], reverse=True):
            # avoid duplicates on abr
            key = round(a["abr_kbps"])
            if key in seen_abr:
                continue
            seen_abr.add(key)
            size_b = a["size_b"] or est_size_from_bitrate_kbps(a["abr_kbps"], duration)
            audio_formats.append({
                "format_id": a["format_id"],
                "quality": f"{int(round(a['abr_kbps']))} kbps",
                "size_mb": human_size(size_b),
            })

        # If mode == audio and we somehow found nothing, tell user
        if mode == "audio" and not audio_formats:
            flash("No audio-only formats found for this URL.", "warning")
            return redirect(url_for("index"))

        # If mode == video and no video formats, warn
        if mode == "video" and not video_formats:
            flash("No video formats found for this URL.", "warning")
            return redirect(url_for("index"))

        return render_template(
            "select.html",
            url=url,
            title=info.get("title"),
            thumbnail=info.get("thumbnail"),
            duration=info.get("duration"),
            views=info.get("view_count"),
            likes=info.get("like_count"),
            channel=info.get("uploader"),
            subscribers=info.get("channel_follower_count"),
            mode=mode,
            platform=platform,  # just pass the value; your template can show it if needed
            formats=(video_formats if mode == "video" else audio_formats),
        )

    # GET
    return render_template("index.html", platforms=PLATFORMS)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    mode = request.form.get("mode")
    format_id = request.form.get("format_id")

    if not url or not mode or not format_id:
        flash("Invalid download request.", "warning")
        return redirect(url_for("index"))

    # Re-extract to detect if chosen format is progressive (has audio)
    info = fetch_info(url)
    chosen = None
    for f in info.get("formats", []):
        if str(f.get("format_id")) == str(format_id):
            chosen = f
            break

    if not chosen:
        flash("Selected format not found.", "danger")
        return redirect(url_for("index"))

    outtmpl = os.path.join(DOWNLOAD_DIR, f"{uuid.uuid4()}_%(title)s.%(ext)s")
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "outtmpl": outtmpl,
        "noplaylist": True,
    }

    try:
        if mode == "video":
            has_audio = (chosen.get("acodec") not in (None, "none"))
            if has_audio:
                # Progressive: download as-is
                ydl_opts["format"] = format_id
            else:
                # Video-only: merge with bestaudio
                ydl_opts["format"] = f"{format_id}+bestaudio/best"
                ydl_opts["merge_output_format"] = "mp4"
        else:
            # Audio only → extract to mp3
            ydl_opts["format"] = format_id
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(url, download=True)
            out_file = ydl.prepare_filename(res)

        # If audio mode, rename to .mp3 (post-processor output)
        if mode == "audio":
            base, _ = os.path.splitext(out_file)
            out_file = base + ".mp3"
            if not os.path.exists(out_file):
                # Some sites already provide mp3 or m4a without rename
                if os.path.exists(base + ".m4a"):
                    out_file = base + ".m4a"

        return send_file(out_file, as_attachment=True)

    except Exception as e:
        flash(f"Download error: {e}", "danger")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

