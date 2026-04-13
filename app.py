# import torch
# import cv2
# import os
# import io
# import pyttsx3
# import numpy as np
# from PIL import Image
# from flask import Flask, render_template, request, url_for, redirect, Response
# import sqlite3
# import threading
# import pythoncom
# from object_info import object_descriptions

# # -------------------- FLASK --------------------
# app = Flask(__name__)
# app.secret_key = 'secret123'

# # -------------------- MODEL --------------------
# MODEL_PATH = r"Yolo V5 - csl_results\best.pt"

# model = torch.hub.load(
#     r"C:\Users\anjum\OneDrive\Desktop\FINEGRAINED - Copy_pre1\yolov5",
#     "custom",
#     path=MODEL_PATH,
#     source="local"
# )
# model.to("cpu")

# # -------------------- VIDEO --------------------
# def gen():
#     cap = cv2.VideoCapture(0)
#     while cap.isOpened():
#         success, frame = cap.read()
#         if not success:
#             break

#         img = Image.fromarray(frame)
#         results = model(img, size=640, conf=0.6)

#         img = np.squeeze(results.render())
#         img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

#         frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video')
# def video():
#     return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# # -------------------- VOICE --------------------
# def speak_text(text):
#     pythoncom.CoInitialize()
#     engine = pyttsx3.init()
#     engine.setProperty('rate', 150)
#     engine.setProperty('volume', 1.0)
#     engine.say(text)
#     engine.runAndWait()
#     pythoncom.CoUninitialize()

# # -------------------- PREDICT --------------------
# @app.route("/predict", methods=["POST", "GET"])
# def predict():
#     if request.method == "POST":
#         file = request.files["file"]
#         img = Image.open(io.BytesIO(file.read()))

#         # Object detection
#         results = model(img, size=640, conf=0.6)
#         detections = results.pandas().xyxy[0]

#         # Unique objects only
#         unique_objects = list(set(detections["name"]))

#         object_info_list = []
#         speech_text = ""

#         for obj in unique_objects:
#             desc = object_descriptions.get(obj, "No description available.")
            
#             object_info_list.append({
#                 "name": obj,
#                 "description": desc
#             })

#             speech_text += f"{obj}. {desc}. "

#         # Voice output
#         if unique_objects:
#             threading.Thread(target=speak_text, args=(speech_text,)).start()

#         # Draw boxes
#         rendered_img = np.squeeze(results.render())
#         rendered_img = cv2.cvtColor(rendered_img, cv2.COLOR_RGB2BGR)

#         # Save image
#         if not os.path.exists("static"):
#             os.makedirs("static")

#         output_path = "static/result.jpg"
#         cv2.imwrite(output_path, rendered_img)

#         return render_template(
#             "detected.html",
#             image_url=output_path,
#             object_info_list=object_info_list
#         )

#     return render_template("index.html")

# # -------------------- PAGES --------------------
# @app.route('/')
# def home():
#     return render_template("home.html")

# @app.route('/index')
# def index():
#     return render_template("index.html")

# @app.route('/login')
# def login():
#     return render_template("signin.html")

# @app.route('/signup')
# def signup_page():
#     return render_template("signup.html")

# # -------------------- SIGNUP --------------------
# @app.route("/signup", methods=["POST"])
# def signup():
#     username = request.form.get("user")
#     name = request.form.get("name")
#     email = request.form.get("email")
#     number = request.form.get("mobile")
#     password = request.form.get("password")

#     con = sqlite3.connect('signup.db')
#     cur = con.cursor()
#     cur.execute(
#         "INSERT INTO info (user, email, password, mobile, name) VALUES (?, ?, ?, ?, ?)",
#         (username, email, password, number, name)
#     )
#     con.commit()
#     con.close()

#     return render_template("signin.html")

# # -------------------- LOGIN --------------------
# @app.route("/signin", methods=["GET", "POST"])
# def signin():
#     if request.method == "POST":
#         username = request.form.get("user")
#         password = request.form.get("password")

#         con = sqlite3.connect("signup.db")
#         cur = con.cursor()
#         cur.execute("SELECT * FROM info WHERE user=? AND password=?", (username, password))
#         data = cur.fetchone()
#         con.close()

#         if data:
#             return redirect(url_for("index"))
#         else:
#             return render_template("signin.html", error="Invalid credentials")

#     return render_template("signin.html")

# # -------------------- RUN --------------------
# if __name__ == "__main__":
#     app.run(debug=True)

import torch
import cv2
import os
import io
import pyttsx3
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, url_for, redirect, Response
import sqlite3
import threading
import pythoncom
from object_info import object_descriptions

# -------------------- FLASK --------------------
app = Flask(__name__)
app.secret_key = 'secret123'

# -------------------- MODEL --------------------
MODEL_PATH = r"Yolo V5 - csl_results\best.pt"

model = torch.hub.load(
    r"C:\Users\anjum\OneDrive\Desktop\FINEGRAINED - Copy_pre1\yolov5",
    "custom",
    path=MODEL_PATH,
    source="local"
)

model.to("cpu")
model.conf = 0.6   # ✅ FIX 1: set confidence globally (instead of passing in forward)

# -------------------- VIDEO --------------------
def gen():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        img = Image.fromarray(frame)

        # ❌ OLD: results = model(img, size=640, conf=0.6)
        # ✅ FIX:
        results = model(img, size=640)

        img = np.squeeze(results.render())
        img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ✅ OPTIONAL FIX: release camera properly
    cap.release()


@app.route('/video')
def video():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# -------------------- VOICE --------------------
def speak_text(text):
    pythoncom.CoInitialize()
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    pythoncom.CoUninitialize()

# -------------------- PREDICT --------------------
@app.route("/predict", methods=["POST", "GET"])
def predict():
    if request.method == "POST":
        file = request.files["file"]

        # ✅ FIX 2: handle empty file safely
        if file.filename == '':
            return redirect(request.url)

        img = Image.open(io.BytesIO(file.read())).convert("RGB")

        # ❌ OLD: results = model(img, size=640, conf=0.6)
        # ✅ FIX:
        results = model(img, size=640)

        detections = results.pandas().xyxy[0]

        # Unique objects only
        unique_objects = list(set(detections["name"]))

        object_info_list = []
        speech_text = ""

        for obj in unique_objects:
            desc = object_descriptions.get(obj, "No description available.")
            
            object_info_list.append({
                "name": obj,
                "description": desc
            })

            speech_text += f"{obj}. {desc}. "

        # Voice output
        if unique_objects:
            threading.Thread(target=speak_text, args=(speech_text,), daemon=True).start()  # ✅ FIX 3: daemon thread

        # Draw boxes
        rendered_img = np.squeeze(results.render())
        rendered_img = cv2.cvtColor(rendered_img, cv2.COLOR_RGB2BGR)

        # Save image
        if not os.path.exists("static"):
            os.makedirs("static")

        output_path = "static/result.jpg"
        cv2.imwrite(output_path, rendered_img)

        return render_template(
            "detected.html",
            image_url=output_path,
            object_info_list=object_info_list
        )

    return render_template("index.html")

# -------------------- PAGES --------------------
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("signin.html")

@app.route('/signup')
def signup_page():
    return render_template("signup.html")

# -------------------- SIGNUP --------------------
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("user")
    name = request.form.get("name")
    email = request.form.get("email")
    number = request.form.get("mobile")
    password = request.form.get("password")

    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute(
        "INSERT INTO info (user, email, password, mobile, name) VALUES (?, ?, ?, ?, ?)",
        (username, email, password, number, name)
    )
    con.commit()
    con.close()

    return render_template("signin.html")

# -------------------- LOGIN --------------------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("user")
        password = request.form.get("password")

        con = sqlite3.connect("signup.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM info WHERE user=? AND password=?", (username, password))
        data = cur.fetchone()
        con.close()

        if data:
            return redirect(url_for("index"))
        else:
            return render_template("signin.html", error="Invalid credentials")

    return render_template("signin.html")

# -------------------- RUN --------------------
if __name__ == "__main__":
    app.run(debug=True)