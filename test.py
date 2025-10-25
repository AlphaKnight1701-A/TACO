from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

# ---- Initialize hub ----
hub = InventorHub()

# ---- Motors ----
motor_base = Motor(Port.A)
motor_shoulder = Motor(Port.B)
motor_elbow = Motor(Port.C)
motor_gripper = Motor(Port.F)

# ---- Distance sensor ----
#sensor = UltrasonicSensor(Port.E)

# ---- Settings ----
SPEED = 200
BASE_DIRECTION = 1
SHOULDER_DIRECTION = 1
ELBOW_DIRECTION = 1

# ---- Reset angles ----
motor_base.reset_angle(0)
motor_shoulder.reset_angle(0)
motor_elbow.reset_angle(0)
motor_gripper.reset_angle(0)

# ---- Helper: Move to absolute angle ----
def goto_angle(motor, target_angle, direction=1, speed=SPEED):
    """Moves motor to a hub-defined absolute angle."""
    target = target_angle * direction
    print(f"Moving motor to {target}°")
    motor.run_target(speed, target, Stop.HOLD, wait=True)

# ---- BASE MOVEMENT ----
def base_down():
    print("Base → Left (−10°)")
    goto_angle(motor_base, -70, BASE_DIRECTION)

def base_up():
    print("Base → Right (+10°)")
    goto_angle(motor_base, 60, BASE_DIRECTION)

def base_center():
    print("Base → Center (0°)")
    goto_angle(motor_base, 0, BASE_DIRECTION)

# ---- SHOULDER MOVEMENT ----
def shoulder_up():
    print("Shoulder → Up (+15°)")
    goto_angle(motor_shoulder, 90, SHOULDER_DIRECTION)

def shoulder_down():
    print("Shoulder → Down (0°)")
    goto_angle(motor_shoulder, 0, SHOULDER_DIRECTION)

# ---- ELBOW MOVEMENT DoNEEEE ----
def elbow_up():
    print("Elbow → Up (+10°)")
    goto_angle(motor_elbow, 120, ELBOW_DIRECTION)

def elbow_down():
    print("Elbow → Down (0°)")
    goto_angle(motor_elbow, -10, ELBOW_DIRECTION)

# ---- GRIPPER CONTROL ----
def gripper_open():
    print("Opening gripper...")
    motor_gripper.run_target(SPEED, 60, Stop.HOLD, wait=True)

def gripper_close():
    print("Closing gripper...")
    motor_gripper.run_until_stalled(-SPEED, Stop.HOLD, duty_limit=50)

# ---- DEMO ----
print("Starting predefined movement demo!")



# ---- BASE ----
base_up()
wait(700)
base_down()
wait(700)
base_center()
wait(700)

# ---- SHOULDER ----
shoulder_up()
wait(700)
shoulder_down()
wait(700)

# ---- ELBOW ----
elbow_up()
wait(700)
elbow_down()
wait(700)

# ---- GRIPPER ----
gripper_open()
wait(700)
gripper_close()
wait(700)


print("✅ Demo complete! Robot is idle.")
