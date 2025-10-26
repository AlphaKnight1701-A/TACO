# 🤖 Robot Tracking System - Setup Guide

## Prerequisites

✅ **LEGO Hub Requirements:**
- Hub is **powered ON**
- Hub is named **"test"** (or update name in `robot_runner.py` line 9)
- Hub is within **Bluetooth range** (3-10 feet from computer)
- Hub has **Pybricks firmware** installed

✅ **Motor Connections:**
- **Port A**: Base motor (rotates left/right)
- **Port F**: Shoulder motor (moves up/down)

---

## Step-by-Step Instructions

### Step 1: Clear the Commands File

```powershell
python -c "open('commands.txt', 'w', encoding='utf-8').write('')"
```

### Step 2: Start the Robot Bridge (Terminal 1)

```powershell
python robot_runner.py
```

**Expected output:**
```
[Runner] 🤖 Robot command runner started
[Runner] 📂 Monitoring: commands.txt
```

⚠️ **Keep this terminal running** - don't close it!

---

### Step 3: Start the Vision System (Terminal 2)

Open a **new terminal** and run:

```powershell
python main.py --use_robot --target_object bottle
```

**Expected output:**
```
🤖 Robot control enabled
[STARTUP] Target object: bottle
[STARTUP] Center zone: 256.0 to 384.0
```

---

### Step 4: Test the Tracking

1. Hold a **bottle** in front of the camera
2. Move it **left** or **right**
3. Watch the robot rotate to track it!

---

## Expected Behavior

### Terminal 1 (robot_runner.py):
```
[Runner] Running on hub (attempt 1/3): BASE:40
[Runner] ✓ Command successful: BASE:40
```

### Terminal 2 (main.py):
```
⬅️  LEFT
📤 SENT: BASE:-40

➡️  RIGHT
📤 SENT: BASE:40
```

---

## System Configuration

| Setting | Value |
|---------|-------|
| **BASE movement** | ±40° |
| **SHOULDER movement** | ±20° |
| **Motor speed** | 1500 deg/s |
| **Command cooldown** | 0.05s (20 commands/sec) |
| **Center threshold** | 20% of frame width |

---

## Troubleshooting

### ❌ UTF-8 Encoding Errors

```
[Runner] Error: 'utf-8' codec can't decode byte 0xff
```

**Fix:**
```powershell
python -c "open('commands.txt', 'w', encoding='utf-8').write('')"
```

---

### ❌ Hub Not Found

```
[HUB] TimeoutError
[HUB] Searching for test...
```

**Fix:**
- Check hub is **powered ON**
- Check hub name is **"test"**
- Move hub **closer** to computer (within 10 feet)
- Make sure hub isn't connected to another device

---

### ❌ Camera Not Opening

```
Could not open camera at index 0
```

**Fix:**
```powershell
python webcam.py  # Find correct camera index
python main.py --use_robot --target_object bottle --camera_index 1  # Use different index
```

---

### ❌ No Movement

**Checklist:**
- [ ] Both terminals are running
- [ ] `robot_runner.py` shows "✓ Command successful"
- [ ] Hub motors are in correct ports (A=base, F=shoulder)
- [ ] Bottle is visible in camera feed
- [ ] Bluetooth connection is stable

---

## Files in the System

| File | Purpose |
|------|---------|
| `main.py` | Vision detection and command generation |
| `robot_runner.py` | Bluetooth bridge to send commands to hub |
| `robot_hub.py` | Hub-side script that controls motors |
| `commands.txt` | Temporary file for command communication |
| `commands_log.txt` | Log of all commands sent (optional) |

---

## Quick Reference - Command Format

Commands written to `commands.txt`:

```
BASE:40       # Rotate base right 40°
BASE:-40      # Rotate base left 40°
SHOULDER_UP   # Move shoulder up 20°
SHOULDER_DOWN # Move shoulder down 20°
STOP          # Stop all motors
```

---

## Notes

⚠️ **Never use `echo` to write to `commands.txt`** - it creates UTF-16 files which cause errors

✅ Only let Python write to the file, or use:
```powershell
python -c "open('commands.txt', 'w', encoding='utf-8').write('BASE:40')"
```

---

## Installation

### Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### Required Packages:
- `ultralytics` - YOLOv8 object detection
- `opencv-python` - Computer vision and camera handling
- `pybricksdev` - LEGO hub Bluetooth communication
- `supervision` - Detection utilities

---

## Support

If issues persist:
1. Restart both terminals
2. Power cycle the LEGO hub
3. Clear commands file again
4. Check Bluetooth connectivity

---

## Architecture Overview

```
┌─────────────┐          ┌──────────────┐         ┌─────────────┐
│   Camera    │─────── ▶│   main.py    │────────▶│commands.txt │
│  (Bottle)   │          │  (YOLOv8)    │         │             │
└─────────────┘          └──────────────┘         └──────┬──────┘
                                                         │
                        ┌──────────────┐                 │
                        │robot_runner  │◀───────────────┘
                        │    .py       │
                        └──────┬───────┘
                               │ Bluetooth
                        ┌──────▼───────┐
                        │  LEGO Hub    │
                        │ (robot_hub)  │
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │    Motors    │
                        │ A=Base F=Arm │
                        └──────────────┘
```

---

## License

MIT License - Feel free to use and modify!

## Contributors

Built with ❤️ for LEGO Mindstorms robot tracking


