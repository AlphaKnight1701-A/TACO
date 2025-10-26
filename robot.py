from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

# ---- Initialize hub ----
hub = InventorHub()

# ---- Motors ----
motor_base = Motor(Port.A)
motor_shoulder = Motor(Port.B)
motor_elbow = Motor(Port.C)
motor_gripper = Motor(Port.F)

# ---- Settings ----
SPEED = 200

# ---- Reset angles ----
motor_base.reset_angle(0)
motor_shoulder.reset_angle(0)
motor_elbow.reset_angle(0)
motor_gripper.reset_angle(0)

# ---- Helper: Move to absolute angle ----
def goto_angle(motor, target_angle, speed=SPEED):
    print(f"Moving motor to {target_angle}°")
    motor.run_target(speed, target_angle, Stop.HOLD, wait=True)

# ---- Quick demo movements ----
print("🤖 Robot connected! Running quick movement demo...")

# Base
goto_angle(motor_base, 45)
wait(500)
goto_angle(motor_base, -45)
wait(500)
goto_angle(motor_base, 0)
wait(500)

# Shoulder
goto_angle(motor_shoulder, 90)
wait(500)
goto_angle(motor_shoulder, 0)
wait(500)

# Elbow
goto_angle(motor_elbow, 90)
wait(500)
goto_angle(motor_elbow, 0)
wait(500)

# Gripper
goto_angle(motor_gripper, 60)
wait(500)
goto_angle(motor_gripper, 0)
wait(500)

print("✅ Quick demo complete! Robot is idle.")
