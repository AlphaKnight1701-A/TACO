from flask import Flask, jsonify, request
import time

app = Flask(__name__)

@app.route('/execute', methods=['POST'])

def execute_action():
    data = request.json
    x, y = data.get('location', [0,0])
    print(f"[TACO] Moving to [{x}, {y}] to pick {data['object']}")
    time.sleep(2) 

    print(f"[TACO] Picked up {data['object']}")
    return jsonify({"status": "success", "message": f"Picked up {data['object']} at location [{x}, {y}]"})

if __name__ == '__main__':
    app.run(port=5003)