from ytmusicapi import YTMusic
from flask import Flask, jsonify

app = Flask(__name__)
ytmusic = YTMusic()

@app.route('/rick-rolled')
def get_rick_rolled():
    try:
        rick = ytmusic.search("Rick Astley - Never Gonna Give You Up")
        return jsonify({"message": "You've been rick-rolled!", "data": rick})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
