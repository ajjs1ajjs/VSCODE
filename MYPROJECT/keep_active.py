import pyautogui
import time
import random

print("🟢 Keep Active started. Ctrl+C to stop.")

pyautogui.FAILSAFE = False

while True:
    
    x, y = pyautogui.position()
    pyautogui.moveTo(x + random.randint(-3, 3), y + random.randint(-3, 3), duration=0.2)

    pyautogui.keyDown('shift')
    time.sleep(0.1)
    pyautogui.keyUp('shift')

    time.sleep(random.randint(60, 120))