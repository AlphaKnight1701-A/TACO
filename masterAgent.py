from shared.message_bus import send_message
from shared.schemas import intent_schema

from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/intent', methods=['POST'])

def intentHandler():
    data = request.json
    print(f"[PLANNER] has Recieved Intent Data: {data}")
    visionResult = requests.post('http://localhost:5002/locate', json=data)
    targetCoordinates = visionResult.json()
    if targetCoordinates:
        tacoInput = {**data, "Object Location": targetCoordinates}
        print(f"[PLANNER] is Sending to [TACO]: {tacoInput}")
        tacoResult = requests.post('http://localhost:5003/execute', json=tacoInput)
    return jsonify ({"status": "[PLANNER] ERROR", "messege": "No target found"})

if __name__ == '__main__':
    app.run(port=5001)




