from ytmusicapi import YTMusic
from flask import Flask, jsonify, Response, stream_with_context, render_template
from flask_cors import CORS
import requests
import logging
import traceback
import urllib.parse
import yt_dlp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
ytmusic = YTMusic()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rick-rolled')
def get_rick_rolled():
    try:
        rick = ytmusic.search("Rick Astley - Never Gonna Give You Up")
        video_id = rick[0]["videoId"]
        return jsonify({"message": "Success", "data": {"videoId": video_id}})
    except Exception as e:
        logger.error(f"Error in rick-rolled: {str(e)}")
        return jsonify({"error": str(e), "message": str(e)}), 500

@app.route('/stream/<video_id>')
def stream_audio(video_id):
    try:
        logger.debug(f"Attempting to stream video ID: {video_id}")
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio[ext=mp3]/bestaudio/best',
            'quiet': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            # Try to find a direct audio file URL (not .m3u8)
            url = None
            flask_mime = None
            mime_type = None
            formats = info.get('formats', [])
            for f in formats:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    fmt_url = f.get('url', '')
                    ext = f.get('ext', '')
                    if '.m3u8' not in fmt_url and ext in ('m4a', 'webm', 'mp3'):
                        url = fmt_url
                        mime_type = ext
                        break
            if not url:
                # fallback to info['url'] if it's not m3u8
                if 'url' in info and '.m3u8' not in info['url']:
                    url = info['url']
                    mime_type = info.get('ext', 'webm')
                else:
                    return jsonify({'error': 'No direct audio stream available for this video.'}), 404
            if mime_type == 'm4a':
                flask_mime = 'audio/mp4'
            elif mime_type == 'mp3':
                flask_mime = 'audio/mpeg'
            else:
                flask_mime = f'audio/{mime_type}'

        logger.debug(f"Stream URL obtained: {url}")
        logger.debug(f"MIME type: {flask_mime}")

        def generate():
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
            except Exception as e:
                logger.error(f"Error during streaming: {str(e)}")
                raise

        response = Response(
            stream_with_context(generate()),
            mimetype=flask_mime,
            headers={
                'Content-Disposition': f'inline; filename={video_id}.{mime_type}',
                'Accept-Ranges': 'bytes',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        return response
    except Exception as e:
        logger.error(f"Error in stream_audio: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/armageddon')
def get_armageddon():
    try:
        results = ytmusic.search("Armageddon - Aespa")
        if not results:
            return jsonify({"error": "No results found"}), 404
        return jsonify({"message": "Armageddon found!", "data": results})
    except Exception as e:
        logger.error(f"Error in armageddon: {str(e)}")
        return jsonify({"error": str(e), "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
