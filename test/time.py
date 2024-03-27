import time
import keyboard

# Frames list
frames = ['frame1', 'frame2', 'frame3', 'frame4']

# Index used to iterate through frames
idx = 0

while True:
    if keyboard.is_pressed('q'): break
    # Delay for 1 second
    time.sleep(1)
    # Print current frame at idx
    print(frames[idx])
    # Increment idx, return to start of list if idx exceeds list length
    idx = (idx + 1) % len(frames)