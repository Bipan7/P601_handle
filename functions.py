from ultralytics import YOLO
import cv2

# ---------------- CONFIG ----------------
MODEL_PATH = "runs/detect/red_green_screw_second_model/weights/best.pt"

roi_x, roi_y, roi_w, roi_h = 200, 150, 300, 200
# ----------------------------------------


# ---------- 1. Capture Frame ----------
def get_frame(cap):
    ret, frame = cap.read()
    return ret, frame


# ---------- 2. Extract ROI ----------
def extract_roi(frame):
    roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    return roi


# ---------- 3. Run Detection ----------
def detect_objects(model, roi):
    results = model(roi, imgsz=320)
    return results


# ---------- 4. Analyze Results ----------
def analyze_results(results):
    roi_center_x = roi_w // 2

    red_on_right = False
    green_on_left = False
    screw_count = 0

    for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
        x1, y1, x2, y2 = box
        class_id = int(cls)

        obj_center_x = int((x1 + x2) / 2)

        if class_id == 1 and obj_center_x > roi_center_x:
            red_on_right = True

        elif class_id == 0 and obj_center_x < roi_center_x:
            green_on_left = True

        elif class_id == 2:
            screw_count += 1

    return red_on_right, green_on_left, screw_count


# ---------- 5. Get Status ----------
def get_status(red_on_right, green_on_left):
    if red_on_right or green_on_left:
        return "OK", (0, 255, 0)
    else:
        return "WRONG", (0, 0, 255)


# ---------- 6. Draw Output ----------
def draw_output(frame, annotated_roi, status, color, screw_count):
    # Put ROI back
    frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w] = annotated_roi

    # Draw ROI box
    cv2.rectangle(frame, (roi_x, roi_y),
                  (roi_x + roi_w, roi_y + roi_h),
                  (0, 255, 0), 2)

    # Draw center line
    roi_center_x = roi_w // 2
    cv2.line(frame,
             (roi_x + roi_center_x, roi_y),
             (roi_x + roi_center_x, roi_y + roi_h),
             (255, 0, 0), 2)

    # Display screw count
    #cv2.putText(frame, f"Screws: {screw_count}",
     #           (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
      #          1, (0, 255, 0), 2)

    # Display status
    #cv2.putText(frame, f"Status: {status}",
     #           (20, 100), cv2.FONT_HERSHEY_SIMPLEX,
      #          1, color, 3)

    return frame


# ---------- MAIN FUNCTION ----------
def main():
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = get_frame(cap)
        if not ret:
            break

        roi = extract_roi(frame)

        results = detect_objects(model, roi)

        annotated_roi = results[0].plot()

        red_on_right, green_on_left, screw_count = analyze_results(results)

        status, color = get_status(red_on_right, green_on_left)

        frame = draw_output(frame, annotated_roi, status, color, screw_count)

        cv2.imshow("Inspection System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------- PROCESS FRAME (for GUI use) ----------
def process_frame(model, frame):
    roi = extract_roi(frame)

    results = detect_objects(model, roi)
    annotated_roi = results[0].plot()

    red_on_right, green_on_left, screw_count = analyze_results(results)
    status, color = get_status(red_on_right, green_on_left)

    frame = draw_output(frame, annotated_roi, status, color, screw_count)

    return frame, status, screw_count