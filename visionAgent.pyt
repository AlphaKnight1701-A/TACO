from flask import Flask, request, jsonify
import cv2

app = Flask(__name__)

@app.route('/locate', methods=['POST'])

def locate_object():

    capture = cv2.VideoCapture(0)
    ret, frame = capture.read()

    if not ret:

        return jsonify({"location": None})
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255))
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        return jsonify({"location": [x, y]})
    return jsonify({"location": None})

if __name__ == "__main__":
    app.run(port=5002)