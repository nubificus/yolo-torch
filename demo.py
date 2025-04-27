from flask import Flask, render_template_string, Response, request
import cv2
import subprocess
import threading
import time
import os
import json

app = Flask(__name__)

stop_event = threading.Event()
# Config
video_path = "traffic_video.mp4"
frame_interval = 1
models = ["yolov5nu-cpu.torchscript", "yolov8n-cpu.torchscript", "yolo11n-cpu.torchscript", "yolov8n-gpu.torchscript"]
executables = {
    "vaccel": "./build/yolo-vaccel",
    "stock": "./build/yolo-stock",
}
env_vars = {
    "default": "bf-GPU",
    "env1": "jetson-GPU",
    "env2": "local-CPU"
}

# Globals
os.makedirs("/dev/shm", exist_ok=True)
cap = cv2.VideoCapture(video_path)
fps_history_stock = []
fps_history_vaccel_local = []
fps_history_vaccel_remote1 = []
fps_history_vaccel_remote2 = []

MAX_HISTORY = 30
current_model = models[0]
current_exec = "vaccel"
current_env_var = "default"
frame = None
lock = threading.Lock()
processing_thread = None
stop_processing = False

def detect_and_annotate(executable, model_path, input_frame):
    resized_frame = cv2.resize(input_frame, (input_frame.shape[1] // 2, input_frame.shape[0] // 2))

    ret, buffer = cv2.imencode('.jpg', resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    if not ret:
        print("Failed to encode frame")
        return input_frame, 0.1

    shm_file = "/dev/shm/temp.jpg"
    with open(shm_file, "wb") as f:
        f.write(buffer)

    # Setup environment dynamically
    env = os.environ.copy()
    if current_env_var == "default":
        env["VACCEL_LOG_LEVEL"] = "3"
        env["VACCEL_PLUGINS"] = "libvaccel-rpc.so"
        env["VACCEL_RPC_ADDRESS"] = "tcp://192.168.4.117:8192"
    elif current_env_var == "env1":
        env["VACCEL_LOG_LEVEL"] = "3"
        env["VACCEL_PLUGINS"] = "libvaccel-rpc.so"
        env["VACCEL_RPC_ADDRESS"] = "tcp://192.168.5.114:8192"
    elif current_env_var == "env2":
        env["VACCEL_LOG_LEVEL"] = "4"
        env["VACCEL_PLUGINS"] = "/home/ananos/develop/vaccel-plugin-torch/build/src/libvaccel-torch.so"

    now = time.time()
    command = [executable, model_path, shm_file]
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    duration = time.time() - now

    output_lines = result.stdout.strip().split("\n")
    for line in output_lines:
        print(line)
        if "<info>" in line and "[prof]" in line and "jitload_forward" in line:
            parts = line.split()
            duration = int(parts[6]) / 1e9
        if "Rect:" in line and "Class:" in line:
            parts = line.split()
            rect_values = parts[1].strip("[]").split(",")
            conf = float(parts[3])
            obj_class = parts[-1]
            x1, y1, x2, y2 = map(int, rect_values)
            color = (0, 255, 0) if obj_class == "person" else (255, 0, 0) if obj_class == "bus" else (0, 0, 255)
            cv2.rectangle(input_frame, (2*x1, 2*y1), (2*x2, 2*y2), color, 2)
            label = f"{obj_class} ({conf:.2f})"
            cv2.putText(input_frame, label, (2*x1, 2*y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return input_frame, duration

def process_frames():
    global frame, fps_history_vaccel, fps_history_stock, cap, stop_processing

    while not stop_event.is_set():
        ret, raw_frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        last_time = time.time()
        processed, duration = detect_and_annotate(executables[current_exec], current_model, raw_frame)
        now = time.time()

        fps2 = 1.0 / (now - last_time)
        fps = 1.0 / duration
        last_time = now

        if current_exec == "stock":
            fps_history_stock.append(fps)
            if len(fps_history_stock) > MAX_HISTORY:
                fps_history_stock.pop(0)
        elif current_exec == "vaccel":
            if current_env_var == "env2":  # Local vaccel
                fps_history_vaccel_local.append(fps)
                if len(fps_history_vaccel_local) > MAX_HISTORY:
                    fps_history_vaccel_local.pop(0)
            elif current_env_var == "default":  # Remote 1 vaccel
                fps_history_vaccel_remote1.append(fps)
                if len(fps_history_vaccel_remote1) > MAX_HISTORY:
                    fps_history_vaccel_remote1.pop(0)
            elif current_env_var == "env1":  # Remote 2 vaccel
                fps_history_vaccel_remote2.append(fps)
                if len(fps_history_vaccel_remote2) > MAX_HISTORY:
                    fps_history_vaccel_remote2.pop(0)

        with lock:
            frame = processed
@app.route('/')
def index():
    return render_template_string('''
<!doctype html>
<title>YOLO Live</title>
<style>
    body { background: #111; color: #eee; font-family: sans-serif; text-align: center; }
    h1 { margin-top: 20px; }
    .controls { margin-bottom: 20px; }
    .video-container { display: flex; flex-direction: column; align-items: center; }
    img { border: 2px solid #444; border-radius: 10px; width: 60vw; }
    canvas { margin-top: 10px; background: #222; border-radius: 8px; }
    select, button { font-size: 1.2em; margin: 10px; }
</style>

<h1>YOLO Model Viewer</h1>
<div class="controls">
    <form action="/set_params" method="post">
        <label>Model:</label>
        <select name="model">
            {% for m in models %}
            <option value="{{ m }}" {% if m == current_model %}selected{% endif %}>{{ m }}</option>
            {% endfor %}
        </select>

        <label>Implementation:</label>
        <select name="exec" id="exec" onchange="toggleEnvDropdown()">
            {% for e in executables %}
            <option value="{{ e }}" {% if e == current_exec %}selected{% endif %}>{{ e }}</option>
            {% endfor %}
        </select>

        <div id="env_dropdown" style="display: {% if current_exec == 'stock' %}none{% else %}block{% endif %};">
            <label>Environment:</label>
            <select name="env_var">
                {% for key, value in env_vars.items() %}
                <option value="{{ key }}" {% if key == current_env_var %}selected{% endif %}>{{ value }}</option>
                {% endfor %}
            </select>
        </div>

        <button type="submit">Apply</button>
    </form>

    <!-- Stop Button -->
    <form action="/stop_processing" method="post">
        <button type="submit">Stop</button>
    </form>
</div>

<div class="video-container">
    <img id="videoFeed" src="/video_feed">
    <canvas id="fpsChart" width="600" height="200"></canvas>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('fpsChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: Array(30).fill(''),
        datasets: [
            {
                label: 'Stock FPS',
                data: [],
                borderColor: 'blue',
                backgroundColor: 'rgba(0,0,255,0.1)',
                tension: 0.4
            },
            {
                label: 'Vaccel Local FPS',
                data: [],
                borderColor: 'green',
                backgroundColor: 'rgba(0,255,0,0.1)',
                tension: 0.4
            },
            {
                label: 'Vaccel Remote1 FPS',
                data: [],
                borderColor: 'orange',
                backgroundColor: 'rgba(255,165,0,0.1)',
                tension: 0.4
            },
            {
                label: 'Vaccel Remote2 FPS',
                data: [],
                borderColor: 'red',
                backgroundColor: 'rgba(255,0,0,0.1)',
                tension: 0.4
            }
        ]
    },
    options: { responsive: false, animation: false, scales: { y: { beginAtZero: true } } }
});

function updateChart() {
    fetch('/fps')
        .then(response => response.json())
        .then(data => {
            chart.data.datasets[0].data = data.stock_fps;
            chart.data.datasets[1].data = data.vaccel_local_fps;
            chart.data.datasets[2].data = data.vaccel_remote1_fps;
            chart.data.datasets[3].data = data.vaccel_remote2_fps;
            chart.update();
        });
}

function toggleEnvDropdown() {
    const exec = document.getElementById('exec').value;
    const envDropdown = document.getElementById('env_dropdown');
    if (exec === 'stock') {
        envDropdown.style.display = 'none';
    } else {
        envDropdown.style.display = 'block';
    }
}

setInterval(updateChart, 1000);
</script>
''', models=models, executables=executables.keys(), current_model=current_model, current_exec=current_exec, env_vars=env_vars, current_env_var=current_env_var)

@app.route('/stop_processing', methods=['POST'])
def stop_processing():
    global stop_processing, stop_event, processing_thread

    # Set the stop event to terminate the processing thread
    stop_event.set()
    if processing_thread and processing_thread.is_alive():
        processing_thread.join()

    stop_processing = True
    return '', 302, {'Location': '/'}




@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            with lock:
                if frame is None:
                    continue
                ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/fps')
def fps():
    return json.dumps({
    "stock_fps": fps_history_stock[-MAX_HISTORY:],
    "vaccel_local_fps": fps_history_vaccel_local[-MAX_HISTORY:],
    "vaccel_remote1_fps": fps_history_vaccel_remote1[-MAX_HISTORY:],
    "vaccel_remote2_fps": fps_history_vaccel_remote2[-MAX_HISTORY:]
    })


@app.route('/set_params', methods=['POST'])
def set_params():
    global current_model, current_exec, current_env_var, cap, processing_thread, stop_processing

    selected_model = request.form.get('model')
    selected_exec = request.form.get('exec')
    selected_env_var = request.form.get('env_var')

    if selected_model in models:
        current_model = selected_model
    if selected_exec in executables:
        current_exec = selected_exec
    if selected_env_var in env_vars:
        current_env_var = selected_env_var

    # Restart processing
    stop_event.set()
    if processing_thread and processing_thread.is_alive():
        processing_thread.join()

    cap.release()
    cap = cv2.VideoCapture(video_path)

    stop_event.clear()
    processing_thread = threading.Thread(target=process_frames)
    processing_thread.start()

    return '', 302, {'Location': '/'}

if __name__ == '__main__':
    #processing_thread = threading.Thread(target=process_frames)
    #processing_thread.start()
    app.run(host='0.0.0.0', debug=True, threaded=True)
