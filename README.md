# Person ROI Detection & Alert System

A basic AI deployment pipeline that detects people in a webcam feed using YOLOv8,
checks whether they enter a defined restricted region (ROI), and raises an alert
— both in the console and on a live web dashboard.

## Features
- Real-time person detection using a pretrained YOLOv8 model (COCO-trained)
- Custom ROI (Region of Interest) overlap logic — detects full or partial overlap
- Live bounding boxes drawn on the video feed, color-coded (green = normal, red = alert)
- Flask backend streaming live video (MJPEG) to a browser-based frontend
- Live dashboard showing person count, alert count, and FPS, polled via a JSON API
- Console alert: `"ALERT: Person in restricted area"` whenever someone enters the ROI

## Project Structure
HumanAI/
├── app.py              # Flask server (routes: /, /video_feed, /stats)
├── main.py             # YOLO detection, ROI logic, frame generator
├── templates/
│   └── index.html      # Frontend dashboard (video feed + live stats)
├── requirements.txt
└── .gitignore

## Setup

1. Clone the repo:
git clone https://github.com/MindtrixAI/person-roi-detection.git
cd person-roi-detection

2. Create a virtual environment:
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux


3. Install dependencies:
python -m pip install -r requirements.txt

4. Run the app:
python app.py

5. Open your browser to:
http://127.0.0.1:5000

   The first run will auto-download the YOLOv8n model weights (~6MB).

## Approach

- **Detection**: Uses YOLOv8n (Ultralytics), the smallest/fastest YOLOv8 variant,
  pretrained on the COCO dataset. Detections are filtered to the "person" class
  (COCO class id 0) with a confidence threshold of 0.5.
- **ROI logic**: The restricted zone is a hardcoded rectangle `(x1, y1, x2, y2)`.
  A detected person's bounding box is considered "inside" the ROI if it overlaps
  or touches it at all. This is computed via an axis-separation check: two
  rectangles overlap unless they are fully separated on the x-axis or the y-axis.
- **Pipeline**: Each webcam frame is read → passed through YOLO → each detected
  person's box is checked against the ROI → boxes are drawn and color-coded →
  the frame is JPEG-encoded and streamed to the browser via Flask using
  `multipart/x-mixed-replace` (MJPEG streaming).
- **Frontend**: A simple HTML/JS dashboard displays the live video feed via an
  `<img>` tag pointed at the streaming endpoint, and polls a `/stats` JSON
  endpoint every 500ms to update live counters (people detected, people in ROI,
  FPS) without reloading the page.

## Limitations

- ROI is a fixed rectangle hardcoded in `main.py` — no UI or config file to set
  it dynamically.
- No object tracking across frames — each frame's detections are independent,
  so an alert prints on every single frame a person overlaps the ROI (no
  de-duplication or cooldown per unique person).
- YOLOv8n prioritizes speed over accuracy — may miss small, partially occluded,
  or fast-moving people. Larger variants (`yolov8s.pt`, `yolov8m.pt`) trade
  speed for accuracy.
- No persistence — alerts are only printed to console/logged in memory, not
  saved to a file or database for later review.
- Assumes a single, static camera — ROI coordinates are in pixel space and
  won't adapt automatically to camera movement or resolution changes.
- Not tested with multiple simultaneous ROIs or multi-camera setups.
- `debug=True` is used for development convenience; not suitable for production
  deployment as-is.

## Possible Improvements
- Add object tracking (e.g. DeepSORT/ByteTrack) to alert once per unique
  person entry rather than every frame.
- Make the ROI configurable via a config file, command-line args, or a UI for
  drawing it directly on the video feed.
- Log alerts with timestamps to a CSV file or database for auditing.
- Support multiple ROIs, each with independent alert messages.