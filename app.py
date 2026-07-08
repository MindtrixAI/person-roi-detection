from flask import Flask, render_template, Response, jsonify
from main import generate_frames, latest_stats

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stats')
def stats():
    return jsonify(latest_stats)


if __name__ == '__main__':
    app.run(debug=True)