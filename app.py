# ================================
#  CarbonVision Raspberry Pi 3B+
#  AI + IoT Emission Detection
# ================================

from flask import Flask, render_template, Response
import cv2, numpy as np, time, paho.mqtt.publish as publish

app = Flask(__name__)

# ----- Configuration -----
CAMERA_INDEX = 0            # usually 0 for USB webcam
MQTT_BROKER_IP = "192.168.x.x"   # <-- put your ESP32 / router IP here
MQTT_TOPIC_ALERT = "/alert"
SMOKE_THRESHOLD = 0.65       # tweak for sensitivity

# ----- Camera setup -----
camera = cv2.VideoCapture(CAMERA_INDEX)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ----- Simple smoke heuristic -----
def detect_smoke(frame):
    """Return confidence 0..1 if smoke-like haze is detected."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    mean = np.mean(blur)
    std = np.std(blur)
    # heuristic: low contrast & medium brightness → likely smoke/haze
    conf = max(0.0, min(1.0, (130 - std) / 80))
    return conf

# ----- Video generator for Flask -----
def gen_frames():
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        conf = detect_smoke(frame)
        status = "Normal"
        color = (0, 255, 0)

        if conf > SMOKE_THRESHOLD:
            status = "Smoke Detected!"
            color = (0, 0, 255)
            try:
                publish.single(MQTT_TOPIC_ALERT, "ALERT=1", hostname=MQTT_BROKER_IP)
            except Exception as e:
                print("MQTT error:", e)

        cv2.putText(frame, f"{status} ({conf:.2f})", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

# ----- Flask routes -----
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
