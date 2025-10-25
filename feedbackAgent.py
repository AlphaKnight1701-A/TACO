import pyttx3
from flask import Flask, request

app = Flask(__name__)
engine = pyttx3.init()

@app.route('/feedback', methods=['POST'])

def feedback():
    message = request.json.get('message', 'No message provided')
    print(f"[FEEDBACK] {message}")
    engine.say(message)
    engine.runAndWait();
    return "Success"

if __name__ == '__main__':
    app.run(port=5004)
