import sys
import time
import subprocess
from pathlib import Path

# Absolute path to the commands file on the PC
COMMANDS_FILE_PATH = Path(r"C:\Users\hackathon\dev\taco\taco-computer-vision\commands.txt")
# Your hub BLE name as seen by pybricksdev - change if needed
HUB_NAME = "test"

# Where to write the temporary action script that will be sent to the hub
TEMP_SCRIPT_PATH = Path(__file__).parent / "_robot_action_temp.py"


def _generate_action_script(command: str) -> str:
    """
    Returns a single-file Pybricks MicroPython program that:
    - initializes motors
    - executes exactly one command (from the PC)
    - stops and exits
    This runs ON THE HUB via `pybricksdev run ble ...`.
    """
    # Keep this template ASCII-only (no emojis).
    return f"""\
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
cmd = "{command}".strip()
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
"""


def _run_command_on_hub(cmd: str, max_retries: int = 3) -> int:
    """Writes a temp script for the given command and runs it via pybricksdev.
    Returns the process return code. Retries on connection failures.
    """
    # Write the temporary script
    TEMP_SCRIPT_PATH.write_text(_generate_action_script(cmd), encoding="utf-8")

    run_cmd = [
        sys.executable,
        "-m", "pybricksdev",
        "run", "ble",
        "-n", HUB_NAME,
        str(TEMP_SCRIPT_PATH)
    ]
    
    for attempt in range(1, max_retries + 1):
        print(f"[Runner] Running on hub (attempt {attempt}/{max_retries}): {cmd}")
        try:
            proc = subprocess.Popen(
                run_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            # Stream output
            if proc.stdout is not None:
                for line in proc.stdout:
                    if line:
                        print(f"[HUB] {line.rstrip()}")
            rc = proc.wait()
            
            if rc == 0:
                print(f"[Runner] ✓ Command succeeded: {cmd}")
                return 0
            else:
                print(f"[Runner] ✗ Command failed (rc={rc}): {cmd}")
                if attempt < max_retries:
                    print(f"[Runner] Retrying in 2 seconds...")
                    time.sleep(2)
                    
        except Exception as e:
            print(f"[Runner] Exception on attempt {attempt}: {e}")
            if attempt < max_retries:
                print(f"[Runner] Retrying in 2 seconds...")
                time.sleep(2)
    
    print(f"[Runner] ✗ All {max_retries} attempts failed for: {cmd}")
    return 1


def main():
    print(f"[Runner] Watching commands file: {COMMANDS_FILE_PATH}")
    print(f"[Runner] Hub name: {HUB_NAME}")
    # Ensure commands file exists
    COMMANDS_FILE_PATH.touch(exist_ok=True)

    while True:
        try:
            # Read and strip commands
            lines = [ln.strip() for ln in COMMANDS_FILE_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if lines:
                print(f"[Runner] Found {len(lines)} command(s)")
                for cmd in lines:
                    rc = _run_command_on_hub(cmd)
                    if rc != 0:
                        print(f"[Runner] Command failed (rc={rc}): {cmd}")
                        # On failure, stop processing remaining commands to avoid spamming reconnects
                        break
                # Clear file after processing (best effort)
                try:
                    COMMANDS_FILE_PATH.write_text("", encoding="utf-8")
                except Exception as e:
                    print(f"[Runner] Failed to clear commands file: {e}")
            # Wait 1s between polls
            time.sleep(1.0)
        except KeyboardInterrupt:
            print("[Runner] Stopping")
            break
        except Exception as e:
            print(f"[Runner] Error: {e}")
            time.sleep(1.0)


if __name__ == "__main__":
    main()
