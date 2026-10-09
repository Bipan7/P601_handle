"""
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import functions as main
from datetime import datetime
import csv
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS   # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ---------------- CONFIG ----------------
#MODEL_PATH = "runs/detect/red_green_screw_second_model/weights/best.pt"
MODEL_PATH = resource_path("runs/detect/red_green_screw_second_model/weights/best.pt")
model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera not accessible")

running = False
current_frame = None

# ---------------- LOG SETUP ----------------
LOG_FILE = "inspection_log.csv"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Status", "Screw Count", "Image Name", "Reason"])

# ---------------- CLEAN OLD LOGS ----------------
def clean_old_logs():
    if not os.path.exists(LOG_FILE):
        return

    updated_rows = []
    cutoff_date = datetime.now() - timedelta(days=30)

    with open(LOG_FILE, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)
        updated_rows.append(header)

        for row in reader:
            try:
                log_date = datetime.strptime(row[0], "%d-%m-%Y %H:%M:%S")
                if log_date >= cutoff_date:
                    updated_rows.append(row)
            except:
                continue

    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

# Run once at startup
clean_old_logs()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("P601 PDI Inspection")
#root.state('zoomed')
root.attributes('-fullscreen', True)
root.resizable(False, False)

# ---------------- HEADER ----------------
header_frame = tk.Frame(root, height=80, bd=2, relief="solid")
header_frame.pack(side="top", fill="x")

# Logo (LEFT)
logo_header_img = Image.open(resource_path("jay_logo.png")).resize((120, 120))  # <-- add your logo file
logo_header_photo = ImageTk.PhotoImage(logo_header_img)

logo_label = tk.Label(header_frame, image=logo_header_photo)
logo_label.pack(side="left", padx=20)

# Project Name (CENTER)
project_label = tk.Label(header_frame,
                         text="P601 PDI Inspection",
                         font=("Arial", 28, "bold"))
project_label.place(relx=0.5, rely=0.5, anchor="center")

# Date-Time (RIGHT)
datetime_label = tk.Label(header_frame, font=("Arial", 14))
datetime_label.pack(side="right", padx=20)

# ---------------- FRAMES ----------------
left_frame = tk.Frame(root, width=400, bd=2, relief="solid")
left_frame.pack(side="left", fill="y")

right_frame = tk.Frame(root, bd=2, relief="solid")
right_frame.pack(side="right", fill="both", expand=True)

logo_frame = tk.Frame(left_frame, height=250, bd=2, relief="solid")
logo_frame.pack(fill="x")

demo_frame = tk.Frame(left_frame, height=250, bd=2, relief="solid")
demo_frame.pack(fill="x")

demo_frame2 = tk.Frame(left_frame, height=250, bd=2, relief="solid")
demo_frame2.pack(fill="x")

#status_frame = tk.Frame(left_frame, height=250, bd=2, relief="solid")
#status_frame.pack(fill="both", expand=True)

video_container = tk.Frame(right_frame)
video_container.pack(side="top", fill="both", expand=True)

live_frame = tk.Frame(video_container, bd=2, relief="solid")
live_frame.pack(side="left", padx=5, pady=5)

result_frame = tk.Frame(video_container, bd=2, relief="solid")
result_frame.pack(side="right", padx=5, pady=5)

status_frame = tk.Frame(right_frame, height=100, bd=1, relief="solid")
status_frame.pack(side="bottom", fill="x")

button_frame = tk.Frame(right_frame, height=100, bd=2, relief="solid")
button_frame.pack(side="bottom", fill="x")

# ---------------- CONTENT ----------------

logo_frame.config(width=250, height=250)
logo_frame.pack_propagate(False)  # 🔴 prevent shrinking

text_label = tk.Label(logo_frame,
                      text="REFERENCE\nIMAGES",
                      font=("Arial", 18, "bold"),
                      justify="center")
text_label.pack(expand=True)

demo_img = Image.open(resource_path("red.jpg")).resize((250, 250))
demo_photo = ImageTk.PhotoImage(demo_img)
tk.Label(demo_frame, image=demo_photo).pack(pady=10)

demo_img2 = Image.open(resource_path("green.jpg")).resize((250, 250))
demo_photo2 = ImageTk.PhotoImage(demo_img2)
tk.Label(demo_frame2, image=demo_photo2).pack(pady=10)

status_label = tk.Label(status_frame,
                        text="STATUS\n---",
                        font=("Arial", 24, "bold"),
                        fg="white",
                        bg="gray",   # default
                        width=15,
                        height=6)
status_label.pack(expand=True, fill="both")

live_label = tk.Label(live_frame)
live_label.pack()

result_label = tk.Label(result_frame)
result_label.pack()

# ---------------- FUNCTIONS ----------------

def update_datetime():
    now = datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
    datetime_label.config(text=now)
    root.after(1000, update_datetime)


def start():
    global running
    running = True
    update_frame()


def stop():
    global running
    running = False
    cap.release()
    root.destroy()


def update_frame():
    global running, current_frame

    if not running:
        return

    if not cap.isOpened():
        print("Camera disconnected!")
        return

    ret, frame = cap.read()
    if not ret:
        return

    current_frame = frame.copy()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img = img.resize((500, 400))
    imgtk = ImageTk.PhotoImage(image=img)

    live_label.imgtk = imgtk
    live_label.configure(image=imgtk)

    live_label.after(10, update_frame)


def capture():
    global current_frame

    if current_frame is None or not cap.isOpened():
        status_label.config(
            text="STATUS\nNO FRAME",
            bg="orange",
            fg="black"
        )
        return

    # Show processing state
    status_label.config(
        text="STATUS\nPROCESSING...",
        bg="yellow",
        fg="black"
    )
    root.update()

    try:
        processed_frame, status, screw_count = main.process_frame(model, current_frame)
    except Exception as e:
        print("Processing error:", e)
        status_label.config(
            text="STATUS\nERROR",
            bg="orange",
            fg="black"
        )
        return

    # Validate output
    if screw_count is None or status is None:
        status_label.config(
            text="STATUS\nINVALID",
            bg="orange",
            fg="black"
        )
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    image_name = f"{timestamp}.jpg"
    save_path = os.path.join(FAIL_DIR, image_name)

    final_status = "PASS"
    reason = "OK"

    EXPECTED_COUNT = 2

    # ---------------- LOGIC ----------------
    if screw_count != EXPECTED_COUNT:
        final_status = "FAIL"
        reason = "Wrong Count"
        status_label.config(
            text=f"STATUS\nFAIL\nCount: {screw_count}",
            bg="red",
            fg="white"
        )

    else:
        if status == "OK":
            final_status = "PASS"
            reason = "OK"
            status_label.config(
                text="STATUS\nPASS",
                bg="green",
                fg="white"
            )
        else:
            final_status = "FAIL"
            reason = "Position/Color Issue"
            status_label.config(
                text="STATUS\nFAIL\nPosition/Color",
                bg="red",
                fg="white"
            )

    # Save only FAIL images
    if final_status == "FAIL" and processed_frame is not None:
        cv2.imwrite(save_path, processed_frame)

    # Log
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            final_status,
            screw_count,
            image_name if final_status == "FAIL" else "N/A",
            reason
        ])

    # Display result
    frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img = img.resize((500, 400))
    imgtk = ImageTk.PhotoImage(image=img)

    result_label.imgtk = imgtk
    result_label.configure(image=imgtk)


# ---------------- BUTTONS ----------------
start_btn = tk.Button(button_frame, text="START",
                      command=start, bg="green", fg="white",
                      font=("Arial", 14), width=10)
start_btn.pack(side="left", padx=30, pady=20)

capture_btn = tk.Button(button_frame, text="CAPTURE",
                        command=capture, bg="blue", fg="white",
                        font=("Arial", 14), width=10)
capture_btn.pack(side="left", padx=30)

stop_btn = tk.Button(button_frame, text="STOP",
                     command=stop, bg="red", fg="white",
                     font=("Arial", 14), width=10)
stop_btn.pack(side="right", padx=30)

# ---------------- RUN ----------------
update_datetime()
root.mainloop()

"""

import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import functions as main
from datetime import datetime, timedelta
import csv
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------- CONFIG ----------------
MODEL_PATH = resource_path("runs/detect/red_green_screw_second_model/weights/best.pt")
model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera not accessible")

running = False
current_frame = None

# ---------------- LOG SETUP ----------------
LOG_FILE = "inspection_log.csv"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Status", "Screw Count", "Image Name", "Reason"])

# ---------------- CLEAN OLD LOGS ----------------
def clean_old_logs():
    if not os.path.exists(LOG_FILE):
        return

    updated_rows = []
    cutoff_date = datetime.now() - timedelta(days=30)

    with open(LOG_FILE, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)
        updated_rows.append(header)

        for row in reader:
            try:
                log_date = datetime.strptime(row[0], "%d-%m-%Y %H:%M:%S")
                if log_date >= cutoff_date:
                    updated_rows.append(row)
            except:
                continue

    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

# Run once at startup
clean_old_logs()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("P601 PDI Inspection")
root.attributes('-fullscreen', True)
root.resizable(False, False)

# ---------------- HEADER ----------------
header_frame = tk.Frame(root, height=80, bd=2, relief="solid")
header_frame.pack(side="top", fill="x")

logo_header_img = Image.open(resource_path("jay_logo.png")).resize((120, 120))
logo_header_photo = ImageTk.PhotoImage(logo_header_img)

logo_label = tk.Label(header_frame, image=logo_header_photo)
logo_label.pack(side="left", padx=20)

project_label = tk.Label(header_frame,
                         text="P601 PDI Inspection",
                         font=("Arial", 28, "bold"))
project_label.place(relx=0.5, rely=0.5, anchor="center")

datetime_label = tk.Label(header_frame, font=("Arial", 14))
datetime_label.pack(side="right", padx=20)

# ---------------- FRAMES ----------------
left_frame = tk.Frame(root, width=400, bd=2, relief="solid")
left_frame.pack(side="left", fill="y")

right_frame = tk.Frame(root, bd=2, relief="solid")
right_frame.pack(side="right", fill="both", expand=True)

logo_frame = tk.Frame(left_frame, height=250, bd=2, relief="solid")
logo_frame.pack(fill="x")

demo_frame = tk.Frame(left_frame, height=250, bd=2, relief="solid")
demo_frame.pack(fill="x")

demo_frame2 = tk.Frame(left_frame, height=250, bd=2, relief="solid")
demo_frame2.pack(fill="x")

video_container = tk.Frame(right_frame)
video_container.pack(side="top", fill="both", expand=True)

live_frame = tk.Frame(video_container, bd=2, relief="solid")
live_frame.pack(side="left", padx=5, pady=5)

result_frame = tk.Frame(video_container, bd=2, relief="solid")
result_frame.pack(side="right", padx=5, pady=5)

status_frame = tk.Frame(right_frame, height=100, bd=1, relief="solid")
status_frame.pack(side="bottom", fill="x")

button_frame = tk.Frame(right_frame, height=100, bd=2, relief="solid")
button_frame.pack(side="bottom", fill="x")

# ---------------- CONTENT ----------------
logo_frame.config(width=250, height=250)
logo_frame.pack_propagate(False)

text_label = tk.Label(logo_frame,
                      text="REFERENCE\nIMAGES",
                      font=("Arial", 18, "bold"),
                      justify="center")
text_label.pack(expand=True)

demo_img = Image.open(resource_path("red.jpg")).resize((250, 250))
demo_photo = ImageTk.PhotoImage(demo_img)
tk.Label(demo_frame, image=demo_photo).pack(pady=10)

demo_img2 = Image.open(resource_path("green.jpg")).resize((250, 250))
demo_photo2 = ImageTk.PhotoImage(demo_img2)
tk.Label(demo_frame2, image=demo_photo2).pack(pady=10)

status_label = tk.Label(status_frame,
                        text="STATUS\n---",
                        font=("Arial", 24, "bold"),
                        fg="white",
                        bg="gray",
                        width=15,
                        height=6)
status_label.pack(expand=True, fill="both")

live_label = tk.Label(live_frame)
live_label.pack()

result_label = tk.Label(result_frame)
result_label.pack()

# ---------------- FUNCTIONS ----------------
def update_datetime():
    now = datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
    datetime_label.config(text=now)
    root.after(1000, update_datetime)

def start():
    global running
    running = True
    update_frame()

def stop():
    global running
    running = False
    cap.release()
    root.destroy()

def update_frame():
    global running, current_frame

    if not running:
        return

    if not cap.isOpened():
        print("Camera disconnected!")
        return

    ret, frame = cap.read()
    if not ret:
        return

    current_frame = frame.copy()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img = img.resize((500, 400))
    imgtk = ImageTk.PhotoImage(image=img)

    live_label.imgtk = imgtk
    live_label.configure(image=imgtk)

    live_label.after(10, update_frame)

def capture():
    global current_frame

    if current_frame is None or not cap.isOpened():
        status_label.config(text="STATUS\nNO FRAME", bg="orange", fg="black")
        return

    status_label.config(text="STATUS\nPROCESSING...", bg="yellow", fg="black")
    root.update()

    try:
        processed_frame, status, screw_count = main.process_frame(model, current_frame)
    except Exception as e:
        print("Processing error:", e)
        status_label.config(text="STATUS\nERROR", bg="orange", fg="black")
        return

    if screw_count is None or status is None:
        status_label.config(text="STATUS\nINVALID", bg="orange", fg="black")
        return

    EXPECTED_COUNT = 2
    final_status = "PASS"
    reason = "OK"

    if screw_count != EXPECTED_COUNT:
        final_status = "N/G"
        reason = "Wrong Count"
        status_label.config(text="STATUS\nN/G", bg="red", fg="white")

    else:
        if status == "OK":
            final_status = "PASS"
            reason = "OK"
            status_label.config(text="STATUS\nPASS", bg="green", fg="white")
        else:
            final_status = "N/G"
            reason = "Position/Color Issue"
            status_label.config(text="STATUS\nN/G", bg="red", fg="white")

    # ✅ Clean logs before writing new one
    clean_old_logs()

    # Log entry (no image saving now)
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            final_status,
            screw_count,
            "N/A",
            reason
        ])

    # Display result
    frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img = img.resize((500, 400))
    imgtk = ImageTk.PhotoImage(image=img)

    result_label.imgtk = imgtk
    result_label.configure(image=imgtk)

# ---------------- BUTTONS ----------------
start_btn = tk.Button(button_frame, text="START",
                      command=start, bg="green", fg="white",
                      font=("Arial", 14), width=10)
start_btn.pack(side="left", padx=30, pady=20)

capture_btn = tk.Button(button_frame, text="CAPTURE",
                        command=capture, bg="blue", fg="white",
                        font=("Arial", 14), width=10)
capture_btn.pack(side="left", padx=30)

stop_btn = tk.Button(button_frame, text="STOP",
                     command=stop, bg="red", fg="white",
                     font=("Arial", 14), width=10)
stop_btn.pack(side="right", padx=30)

# ---------------- RUN ----------------
update_datetime()
root.mainloop()

