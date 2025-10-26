"""
Robot hub program - runs ON the LEGO hub via pybricksdev.
Initializes and then waits for movement commands from a text file.
"""

from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait
# Add sys for stdin-based command streaming
try:
    import sys
except ImportError:
    sys = None

# ---- Initialize hub ----
hub = InventorHub()
HUB_NAME = "test"

# ---- Motors ----
motor_base = Motor(Port.B)
motor_shoulder = Motor(Port.F)
motor_elbow = Motor(Port.C)
motor_gripper = Motor(Port.A)

# ---- Settings ----
SPEED =  500 # ULTRA FAST for instant tracking response
GRIPPER_CLOSE_SPEED = -200
GRIPPER_OPEN_SPEED = 200
GRIPPER_DUTY_LIMIT = 50
POLL_INTERVAL = 1000  # milliseconds

# ---- Motor bounds (degrees) ----
SHOULDER_MIN = 0
SHOULDER_MAX = 90
BASE_MIN = 0
BASE_MAX = 360
ELBOW_MIN = 0
ELBOW_MAX = 120
GRIPPER_OPEN_ANGLE = 60

# ---- Reset angles on start ----
motor_base.reset_angle(0)
motor_shoulder.reset_angle(0)
motor_elbow.reset_angle(0)
motor_gripper.reset_angle(0)

print("Robot hub initialized!")

# ---- Incremental Movement Function ----
def move_motor_by(motor, delta, min_angle, max_angle):
    current_angle = motor.angle()
    target_angle = current_angle + delta
    if target_angle > max_angle: target_angle = max_angle
    elif target_angle < min_angle: target_angle = min_angle
    print(f"Moving motor from {current_angle} to {target_angle} deg")
    motor.run_target(SPEED, target_angle, Stop.HOLD, wait=False)

# ---- Command execution ----
def execute_command(command):
    command = command.strip()
    if not command:
        return
    print(f"Executing command: {command}")
    
    try:
        if command.upper() == 'STOP':
            print("STOPPING ALL MOTORS")
            motor_base.stop()
            motor_shoulder.stop()
            motor_elbow.stop()
        elif command.upper() == 'SHOULDER_UP':
            print("Executing command: SHOULDER_UP")
            move_motor_by(motor_shoulder, 20, SHOULDER_MIN, SHOULDER_MAX)
        elif command.upper() == 'SHOULDER_DOWN':
            print("Executing command: SHOULDER_DOWN")
            move_motor_by(motor_shoulder, -20, SHOULDER_MIN, SHOULDER_MAX)
        else:
            parts = command.split(':')
            if len(parts) >= 2:
                motor_name = parts[0].upper()
                
                # Handle angle-based commands (SIMPLE AND PROVEN)
                try:
                    delta = int(parts[1])
                except Exception:
                    print(f"Invalid delta in command '{command}'")
                    return
                
                if motor_name == "BASE":
                    move_motor_by(motor_base, delta, BASE_MIN, BASE_MAX)
                elif motor_name == "SHOULDER":
                    move_motor_by(motor_shoulder, delta, SHOULDER_MIN, SHOULDER_MAX)
                elif motor_name == "ELBOW":
                    move_motor_by(motor_elbow, delta, ELBOW_MIN, ELBOW_MAX)
                elif motor_name == "GRIPPER":
                    if delta > 0:
                        print("Gripper: Opening")
                        motor_gripper.run_target(GRIPPER_OPEN_SPEED, GRIPPER_OPEN_ANGLE, Stop.HOLD, wait=False)
                    else:
                        print("Gripper: Closing until stalled")
                        motor_gripper.run_until_stalled(GRIPPER_CLOSE_SPEED, then=Stop.HOLD, duty_limit=GRIPPER_DUTY_LIMIT)
                else:
                        print(f"Unknown motor '{motor_name}'")
            else:
                print(f"Unrecognized command format: '{command}'")
    except Exception as e:
        print(f"Error processing command: {e}")

# ---- Main loop: listen for commands from host via stdin ----
if sys is not None and hasattr(sys, "stdin"):
    print("Robot ready! Listening for commands from host (stdin)...")
    try:
        # Iterate over incoming lines from the host; each line is one command
        for line in sys.stdin:
            if not line:
                # End of stream
                break
            execute_command(line)
            # Small wait to keep the scheduler responsive
            wait(10)
    except KeyboardInterrupt:
        pass
else:
    # Stdin not available on this runtime; cannot receive commands dynamically.
    print("WARNING: sys.stdin is not available on this hub runtime. Cannot receive commands from host.")

print("Stopping robot...")
motor_base.stop()
motor_shoulder.stop()
motor_elbow.stop()
motor_gripper.stop()
print("Robot stopped")
