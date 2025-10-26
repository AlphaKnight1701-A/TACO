from ultralytics import YOLO

def main():
    model = YOLO("yolov8l.pt")
    print(model.names)


if __name__ == "__main__":
    main()