from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

# ---- Initialize hub and motors ----
hub = InventorHub()
motor_base = Motor(Port.B)
motor_shoulder = Motor(Port.F)  # Fixed: Was Port.B, should be Port.F
motor_elbow = Motor(Port.C)
motor_gripper = Motor(Port.A)  # Fixed: Was Port.F, should be Port.B

# ---- Settings ----
SPEED = 500  # Increased from 500 to 1000 for faster, more dramatic movements!
GRIPPER_CLOSE_SPEED = -400  # Doubled for faster gripper
GRIPPER_OPEN_SPEED = 400    # Doubled for faster gripper
GRIPPER_DUTY_LIMIT = 50

# ---- Motor bounds (degrees) ----
SHOULDER_MIN = 0
SHOULDER_MAX = 90
BASE_MIN = 0
BASE_MAX = 90
ELBOW_MIN =360
ELBOW_MAX = 120
GRIPPER_OPEN_ANGLE = 60

# ---- Incremental Movement Function ----
def move_motor_by(motor, delta, min_angle, max_angle):
    current_angle = motor.angle()
    target_angle = current_angle + delta
    if target_angle > max_angle:
        target_angle = max_angle
    elif target_angle < min_angle:
        target_angle = min_angle
    print("Moving motor from", current_angle, "to", target_angle, "deg")
    motor.run_target(SPEED, target_angle, Stop.HOLD, wait=True)

# ---- Execute one command ----
cmd = "﻿".strip()
print("Executing command:", cmd)
try:
    if cmd.upper() == 'SHOULDER_UP':
        move_motor_by(motor_shoulder, 30, SHOULDER_MIN, SHOULDER_MAX)  # Tripled from 10 to 30 degrees!
    elif cmd.upper() == 'SHOULDER_DOWN':
        move_motor_by(motor_shoulder, -30, SHOULDER_MIN, SHOULDER_MAX)  # Tripled from -10 to -30 degrees!
    else:
        parts = cmd.split(':')
        if len(parts) >= 2:
            name = parts[0].upper()
            try:
                delta = int(parts[1])
            except Exception:
                print("Invalid delta in command:", cmd)
                delta = None
            if delta is not None:
                if name == 'BASE':
                    move_motor_by(motor_base, delta, BASE_MIN, BASE_MAX)
                elif name == 'SHOULDER':
                    move_motor_by(motor_shoulder, delta, SHOULDER_MIN, SHOULDER_MAX)
                elif name == 'ELBOW':
                    move_motor_by(motor_elbow, delta, ELBOW_MIN, ELBOW_MAX)
                elif name == 'GRIPPER':
                    if delta > 0:
                        print("Gripper: Opening")
                        motor_gripper.run_target(GRIPPER_OPEN_SPEED, GRIPPER_OPEN_ANGLE, Stop.HOLD, wait=False)
                    else:
                        print("Gripper: Closing until stalled")
                        motor_gripper.run_until_stalled(GRIPPER_CLOSE_SPEED, then=Stop.HOLD, duty_limit=GRIPPER_DUTY_LIMIT)
                else:
                    print("Unknown motor:", name)
        else:
            print("Unrecognized command format:", cmd)
except Exception as e:
    print("Error processing command:", e)

# Ensure motors are stopped before exit
try:
    motor_base.stop(); motor_shoulder.stop(); motor_elbow.stop(); motor_gripper.stop()
except Exception:
    pass
print("Done")
