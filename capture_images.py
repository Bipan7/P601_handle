
import cv2
import os

# Folder to save images
save_folder = "red_P"   #chnage name here
os.makedirs(save_folder, exist_ok=True)

# Open camera
cap = cv2.VideoCapture(0)   # 0 for laptop cam

if not cap.isOpened():
    print("Error: Camera not found")
    exit()

img_count = 0

# ROI coordinates (x, y, width, height)
roi_x = 200
roi_y = 150
roi_w = 300
roi_h = 200

print("Press 's' to save ROI image")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Draw ROI rectangle
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0,255,0), 2)

    # Show camera feed
    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    # Save only ROI
    if key == ord('s'):
        roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        filename = os.path.join(save_folder, f"red{img_count}.jpg")  #change here
        cv2.imwrite(filename, roi)
        print(f"Saved: {filename}")
        img_count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()