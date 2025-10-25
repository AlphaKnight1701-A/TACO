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
sensor = UltrasonicSensor(Port.E)

# ---- Settings ----
SPEED = 500
BASE_DIRECTION = -1  # Set to -1 if your base is reversed
OTHER_BASE_DIRECTION = 1

# ---- Showcase Mode Settings ----
SHOWCASE_SPEED = 800

# ---- Functions ----
def gripper_open():
    """Open the gripper."""
    print("Opening gripper...")
    motor_gripper.run_angle(SPEED, 60, Stop.COAST, wait=True)

def gripper_close():
    """Close the gripper."""
    print("Closing gripper...")
    motor_gripper.run_until_stalled(-SPEED, Stop.HOLD, duty_limit=50)

def base_up():
    """Move base up."""
    print("Base up")
    motor_base.run_angle(SPEED, 15 * BASE_DIRECTION, Stop.HOLD, wait=True)

def base_down():
    """Move base down"""
    print("Base down")
    motor_base.run_angle(SPEED, 15 * OTHER_BASE_DIRECTION, Stop.Hold, Wait=True)



def rotate_left():
    """Rotate shoulder to the left."""
    print("Rotating left")
    motor_shoulder.run_angle(SPEED, -30, Stop.COAST, wait=True)

def rotate_right():
    """Rotate shoulder to the right."""
    print("Rotating right")
    motor_shoulder.run_angle(SPEED, 30, Stop.COAST, wait=True)

def elbow_up():
    """Move elbow up."""
    print("Elbow up")
    motor_elbow.run_angle(SPEED, 15, Stop.HOLD, wait=True)

def elbow_down():
    """Move elbow down."""
    print("Elbow down")
    motor_elbow.run_angle(SPEED, -15, Stop.HOLD, wait=True)

# ---- Initialization ----
print("Starting robotic arm showcase!")
print("\nAll tests complete!")

# ---- CRAZY SHOWCASE MODE ----
print("\n=== ENTERING SHOWCASE MODE ===")
print("Robot arm going crazy!")

iteration = 0
while True:
    iteration += 1
    print(f"\n--- Showcase iteration {iteration} ---")
    
    # Combo 1: Big base movements
    print("COMBO 1: Big UP!")
    motor_base.run_angle(SHOWCASE_SPEED, 100 * BASE_DIRECTION, Stop.HOLD, wait=False)
    wait(1000)
    
    # Combo 2: Huge up
    print("COMBO 2: HUGE UP!")
    motor_base.run_angle(SHOWCASE_SPEED, 150 * BASE_DIRECTION, Stop.HOLD, wait=False)
    wait(1000)
    
    # Combo 3: Final big up
    print("COMBO 3: FINAL BIG UP!")
    motor_base.run_angle(SHOWCASE_SPEED, 120 * BASE_DIRECTION, Stop.HOLD, wait=False)
    wait(1000)
    
    print(f"Iteration {iteration} complete! Continuing...")
    wait(500)

print("Program ended.")
