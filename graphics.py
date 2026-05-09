import cv2
import mediapipe as mp
import random
import time

from fruit_entity import Fruit
from graphics import load_fruit, draw_button, button_clicked
from game_mechanics import (GRAVITY, INITIAL_SPAWN_N, MAX_TRAIL, CLICK_DELAY, 
                            line_intersects_circle, calculate_difficulty)

# ---------------------------
# HAND TRACKING SETUP
# ---------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# ---------------------------
# GAME STATE VARIABLES
# ---------------------------
score = 0
game_state = "STOP"
game_start_time = 0
fruits = []
trail_points = []
prev_point = None
last_click_time = 0

# ---------------------------
# LOAD FRUIT ASSETS
# ---------------------------
try:
    fruit_types = [
        load_fruit("or"), load_fruit("wm"), load_fruit("ap"), load_fruit("pn")
    ]
except Exception as e:
    print(f"Error: {e}. Check your 'assets' folder.")
    exit()

# ---------------------------
# WINDOW INITIALIZATION
# ---------------------------
win_name = "Fruit Ninja AI"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

# ---------------------------
# MAIN LOOP
# ---------------------------
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (800, 600))
    h_f, w_f, _ = frame.shape

    # Hand detection
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    finger_x, finger_y = None, None

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            lm = handLms.landmark[8]
            finger_x, finger_y = int(lm.x * w_f), int(lm.y * h_f)
            trail_points.append((finger_x, finger_y))
            if len(trail_points) > MAX_TRAIL:
                trail_points.pop(0)

    # Draw hand trail
    for i in range(1, len(trail_points)):
        cv2.line(frame, trail_points[i-1], trail_points[i], (255, 255, 255), int(i*2))

    # Draw UI buttons
    draw_button(frame, "PLAY", 10, 10, 80, 40, game_state == "PLAY")
    draw_button(frame, "STOP", 100, 10, 80, 40, game_state == "STOP")
    draw_button(frame, "RESET", 190, 10, 90, 40)

    # Handle button clicks
    curr_t = time.time()
    if finger_x is not None and curr_t - last_click_time > CLICK_DELAY:
        if button_clicked(finger_x, finger_y, 10, 10, 80, 40):
            if game_state != "PLAY":
                game_start_time = curr_t
                fruits.clear()
            game_state = "PLAY"
            last_click_time = curr_t
        elif button_clicked(finger_x, finger_y, 100, 10, 80, 40):
            game_state = "STOP"
            last_click_time = curr_t
        elif button_clicked(finger_x, finger_y, 190, 10, 90, 40):
            score = 0
            fruits.clear()
            game_start_time = curr_t
            last_click_time = curr_t

    # Game logic
    if game_state == "PLAY":
        elapsed = curr_t - game_start_time
        difficulty, spawn_n = calculate_difficulty(elapsed)

        if random.randint(1, int(spawn_n)) == 1:
            fruits.append(Fruit(fruit_types, GRAVITY))

        for fruit in fruits[:]:
            fruit.update()
            
            # Check for slicing
            if fruit.state == "whole" and prev_point and finger_x:
                if line_intersects_circle(prev_point, (finger_x, finger_y), fruit.x, fruit.y):
                    fruit.slice()
                    score += 1
            
            fruit.draw(frame)
            
            # Remove fruits that fell off screen
            if fruit.y > 750 or (fruit.state == "cut" and fruit.cut_y > 750):
                if fruit.state == "whole":
                    score = max(0, score - 1)
                if fruit in fruits:
                    fruits.remove(fruit)

    elif game_state == "STOP":
        fruits.clear()

    # Update trail
    prev_point = (finger_x, finger_y) if finger_x else None

    # Draw score
    cv2.putText(frame, f"Score: {score}", (600, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow(win_name, frame)

    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC to quit
        break
    elif key == ord('f'):  # Press 'f' to toggle Fullscreen
        is_full = cv2.getWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN)
        if is_full == cv2.WINDOW_FULLSCREEN:
            cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        else:
            cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

cap.release()
cv2.destroyAllWindows()