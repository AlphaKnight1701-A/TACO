import argparse
import cv2
import time

import supervision as sv
from ultralytics import YOLO


def list_cameras(max_index: int = 10):
    """Try opening camera indices and return a list of indices that opened.

    Uses DirectShow backend on Windows by default when available.
    """
    found = []
    for i in range(max_index):
        # Prefer DirectShow on Windows to get USB webcams consistently
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            found.append(i)
            cap.release()
        else:
            # ensure resource cleaned up
            try:
                cap.release()
            except Exception:
                pass
    return found


def main():
    cams = list_cameras(8)
    if cams:
        print(f"Found cameras at indices: {cams}")
        idx = cams[0]
    else:
        print("No cameras found using DirectShow on indices 0-7; falling back to index 0")
        idx = 0

    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise SystemExit(f"Failed to open camera at index {idx}. Try different indices from `list_cameras()` output or plug the camera in.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to grab frame from camera, retrying...")
            time.sleep(0.1)
            continue

        cv2.imshow('Video Feed', frame)

        # exit on 'q' key
        if cv2.waitKey(27) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()