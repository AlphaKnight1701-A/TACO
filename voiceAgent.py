import speech_recognition as SR
import requests

def getAudioInput():
    recognizer = SR.Recognizer()
    with SR.Microphone() as source:
        print("[VOICE AGENT] Listening for command...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_goole(audio)
        print(f"[VOICE AGENT] Recognized command: {text}")
        return text.tolower()
    except SR.UnknownValueError:
        print("[VOICE AGENT] Could not understand audio")
        return ""
    
def parseCommand(command):
    if "pick up" in command:
        object_name = command.split("pick up")[-1].strip()
    return {"action": "pick_up", "object": object_name}

def sendToMaster(command):
    url = 'http://localhost:5001/master'
    result = requests.post(url, json=command)
    print(f"[VOICE AGENT] Sending to Master Agent: {result.text}")
    
if __name__ == "__main__":
    while True:
        command = getAudioInput()
        if command:
            parsed = parseCommand(command)
            if parsed:
                sendToMaster(parsed)
                
    

