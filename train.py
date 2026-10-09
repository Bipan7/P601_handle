from ultralytics import YOLO

# Load model (smallest + fastest for CPU)
model = YOLO("yolov8n.pt")

# Train
model.train(
    data="dataset/data.yaml",
    epochs=30,
    imgsz=416,
    batch=8,
    device="cpu",
    name="red_green_screw_second_model"
)