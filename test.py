'''from ultralytics import YOLO

model = YOLO("runs/detect/red_green_screw_model/weights/best.pt")

results = model("test.jpg", show=True)

for r in results:
    screw_count = sum(1 for cls in r.boxes.cls if int(cls) == 2)
    print("Screws detected:", screw_count)'''




'''
from ultralytics import YOLO
import cv2

# Load trained model
model = YOLO("runs/detect/red_green_screw_model/weights/best.pt")

# Camera
cap = cv2.VideoCapture(1)

# ROI settings (your values)
roi_x = 200
roi_y = 150
roi_w = 300
roi_h = 200

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Draw ROI box
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0,255,0), 2)

    # Crop ROI
    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]

    # Run detection ONLY on ROI
    results = model(roi, imgsz=320)

    annotated_roi = results[0].plot()

    # Count screws (class 2)
    screw_count = sum(1 for cls in results[0].boxes.cls if int(cls) == 2)

    # Put annotated ROI back into frame
    frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w] = annotated_roi

    # Display screw count
    cv2.putText(
        frame,
        f"Screws: {screw_count}",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("ROI Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()'''



from ultralytics import YOLO
import cv2

# Load trained model
model = YOLO("runs/detect/red_green_screw_second_model/weights/best.pt")

# Open camera
cap = cv2.VideoCapture(0)

# ROI settings
roi_x = 200
roi_y = 150
roi_w = 300
roi_h = 200

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Draw ROI rectangle
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 255, 0), 2)

    # Crop ROI
    roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]

    # Run YOLO on ROI
    results = model(roi, imgsz=320)

    annotated_roi = results[0].plot()

    # ----------- LOGIC START -----------

    roi_center_x = roi_w // 2

    red_on_right = False
    green_on_left = False

    screw_count = 0

    for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
        x1, y1, x2, y2 = box
        class_id = int(cls)

        # center of bounding box
        obj_center_x = int((x1 + x2) / 2)

        if class_id == 1:  # red_part
            if obj_center_x > roi_center_x:
                red_on_right = True

        elif class_id == 0:  # green_part
            if obj_center_x < roi_center_x:
                green_on_left = True

        elif class_id == 2:  # screw
            screw_count += 1

    # Final status
    if red_on_right or green_on_left:
        status = "OK"
        color = (0, 255, 0)
    else:
        status = "WRONG"
        color = (0, 0, 255)

    # ----------- LOGIC END -----------

    # Put annotated ROI back
    frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w] = annotated_roi

    # Draw center line (for visualization)
    cv2.line(frame,
             (roi_x + roi_center_x, roi_y),
             (roi_x + roi_center_x, roi_y + roi_h),
             (255, 0, 0), 2)

    # Display screw count
    cv2.putText(frame, f"Screws: {screw_count}",
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)

    # Display status
    cv2.putText(frame, f"Status: {status}",
                (20, 100), cv2.FONT_HERSHEY_SIMPLEX,
                1, color, 3)

    # Show frame
    cv2.imshow("Inspection System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
