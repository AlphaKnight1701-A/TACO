@echo off
REM Batch script to run the full robot command pipeline
REM 1. Starts robot_runner.py (PC-side, polls commands.txt and runs commands on the hub)
REM 2. Starts main.py (writes commands to commands.txt as needed)
REM Both run in separate windows and keep running until closed manually

REM Start the robot runner in a new window
start "Robot Runner" cmd /k python robot_runner.py

REM Wait a moment to ensure the runner is up
ping 127.0.0.1 -n 2 > nul

REM Start the main vision/controller script in a new window
start "Main Vision" cmd /k python main.py --use_robot --target_object bottle
REM Done. Both windows will stay open until you close them manually.
REM You can add commands to commands.txt at any time, or let main.py do it automatically.
