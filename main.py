import argparse
import cv2
import os

import supervision as sv
from ultralytics import YOLO

# DAVID TEST CODE



def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 Video Capture")
    parser.add_argument(
        '--webcam_resolution',
        default = [640, 480],
        type = int,
        nargs = 2,
        help = 'Webcam resolution width height'
    )
    parser.add_argument(
        '--target_object',
        default=None,
        type=str,
        help='Object name to track (must match a class in names.txt, e.g. "cup", "bottle", "person")'
    )
    parser.add_argument(
        '--center_threshold',
        default=0.2,
        type=float,
        help='Fraction of frame width for center zone (default: 0.2 = 20%% of width centered)'
    )
    parser.add_argument(
        '--use_robot',
        action='store_true',
        help='Enable robot motor control (requires robot_controller module and connected hardware)'
    )
    parser.add_argument(
        '--movement_step',
        default=5,
        type=int,
        help='Degrees to move robot per adjustment (default: 5)'
    )
    return parser.parse_args()

def main():
    args = parse_args()
    frame_width, frame_height = args.webcam_resolution
    frame_center_x = frame_width / 2
    
    # Calculate center zone boundaries
    center_zone_width = frame_width * args.center_threshold
    center_left = frame_center_x - (center_zone_width / 2)
    center_right = frame_center_x + (center_zone_width / 2)

    # Initialize robot if requested
    robot_controller = None
    if args.use_robot:
        print("🤖 Robot control enabled")
        print("   NOTE: Make sure robot_hub.py is already running on the hub!")
        print("   Start it with: python -m pybricksdev run ble -n test robot_hub.py")
        print("   This script will send movement commands via console output.")
        robot_controller = "enabled"  # Simple flag for now

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    # Use OpenCV's bundled haarcascade path so the XML is found reliably
    cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
    cascade = cv2.CascadeClassifier(cascade_path)

    if not cap.isOpened():
        raise SystemExit(f"Could not open camera at index 0. Try running `webcam.py` to enumerate camera indices.")

    if cascade.empty():
        raise SystemExit(f"Failed to load cascade classifier from {cascade_path}. Check your OpenCV installation.")

    model = YOLO("yolov8l.pt")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to read frame from camera, stopping")
            break
        # run yolo model on the frame (keep as color BGR input for YOLO)
        result = model(frame)[0]
        # convert to grayscale for the Haar cascade detector
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        objects, reject_levels, confidence_levels = cascade.detectMultiScale3(
            gray, 
            scaleFactor = 1.1, 
            minNeighbors = 3, 
            outputRejectLevels = True
        )
        # Draw bounding boxes on a copy of the frame
        out = frame.copy()
        # Draw YOLO boxes (support multiple result shapes/backends)
        try:
            xyxy = result.boxes.xyxy.cpu().numpy()
        except Exception:
            try:
                xyxy = result.boxes.xyxy.numpy()
            except Exception:
                # fallback to list-of-lists
                xyxy = getattr(result.boxes, 'xyxy', [])

        # Gather confs and classes if available
        try:
            confs = result.boxes.conf.cpu().numpy()
        except Exception:
            try:
                confs = result.boxes.conf.numpy()
            except Exception:
                confs = getattr(result.boxes, 'conf', [])

        try:
            classes = result.boxes.cls.cpu().numpy()
        except Exception:
            try:
                classes = result.boxes.cls.numpy()
            except Exception:
                classes = getattr(result.boxes, 'cls', [])

        # Draw each YOLO detection
        for i, b in enumerate(xyxy):
            try:
                x1, y1, x2, y2 = map(int, b[:4])
            except Exception:
                continue
            # build label text if class and confidence are available
            label = None
            try:
                cls_i = int(classes[i]) if len(classes) > i else None
            except Exception:
                cls_i = None
            try:
                conf_i = float(confs[i]) if len(confs) > i else None
            except Exception:
                conf_i = None

            if cls_i is not None and conf_i is not None:
                name = model.names.get(cls_i, str(cls_i)) if hasattr(model, 'names') else str(cls_i)
                label = f"{name} {conf_i:.2f}"
            elif conf_i is not None:
                label = f"{conf_i:.2f}"

            # Check if this detection matches the target object
            if args.target_object and cls_i is not None:
                detected_name = model.names.get(cls_i, '').lower() if hasattr(model, 'names') else ''
                if detected_name == args.target_object.lower():
                    # Calculate overlap between bounding box and center zone
                    # Find the intersection between bbox [x1, x2] and center zone [center_left, center_right]
                    overlap_left = max(x1, center_left)
                    overlap_right = min(x2, center_right)
                    overlap_width = max(0, overlap_right - overlap_left)
                    
                    bbox_width = x2 - x1
                    overlap_fraction = overlap_width / bbox_width if bbox_width > 0 else 0
                    
                    # If majority (>50%) of bbox is within center zone, it's centered
                    if overlap_fraction > 0.5:
                        print("Centered")
                        # Robot is already centered, no movement needed
                    else:
                        # Calculate bounding box center for left/right determination
                        bbox_center_x = (x1 + x2) / 2
                        
                        if bbox_center_x < center_left:
                            print("Look left")
                            if robot_controller:
                                # Send command that robot can receive
                                print(f"ROBOT_CMD:SHOULDER:{-args.movement_step}")
                        else:
                            print("Look right")
                            if robot_controller:
                                # Send command that robot can receive
                                print(f"ROBOT_CMD:SHOULDER:{args.movement_step}")

            cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if label:
                cv2.putText(out, label, (x1, max(10, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # Draw Haar cascade face detections (objects is typically an array of rects)
        try:
            for rect in objects:
                # some return shapes: (x, y, w, h)
                if len(rect) >= 4:
                    x, y, w, h = map(int, rect[:4])
                    cv2.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 2)
        except Exception:
            # ignore drawing errors
            pass
        # Show the annotated frame
        cv2.imshow('Video Feed', out)

        # exit on 'q' key
        if cv2.waitKey(27) & 0xFF == ord('q'):
            break
    # end main loop
    cap.release()
    
    # Shutdown message
    if robot_controller:
        print("ROBOT_CMD:STOP")



        

if __name__ == "__main__":
    try:
        main()
    finally:
        # Best-effort cleanup
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass


