import cv2
import random
import math
from graphics import rotate_image, overlay, FRUIT_SIZE

# ---------------------------
# FRUIT CLASS
# ---------------------------
class Fruit:
    def __init__(self, fruit_types, gravity):
        self.x = random.randint(150, 650)
        self.y = 620
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-23, -18)
        self.images = random.choice(fruit_types)
        self.state = "whole"
        self.angle = 0
        self.rotation_speed = random.uniform(-6, 6)
        self.left_x = self.right_x = 0.0
        self.cut_y = self.cut_vy = 0.0
        self.left_vx, self.right_vx = -7.0, 7.0
        self.gravity = gravity

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.angle += self.rotation_speed
        if self.state == "cut":
            self.left_x += self.left_vx
            self.right_x += self.right_vx
            self.cut_vy += self.gravity
            self.cut_y += self.cut_vy

    def draw(self, frame):
        if self.state == "whole":
            img = rotate_image(self.images["whole"], self.angle)
            overlay(frame, img, int(self.x) - FRUIT_SIZE // 2, int(self.y) - FRUIT_SIZE // 2)
        else:
            l_img = rotate_image(self.images["left"], self.angle)
            r_img = rotate_image(self.images["right"], -self.angle)
            by = int(self.cut_y) - FRUIT_SIZE // 2
            overlay(frame, l_img, int(self.left_x) - FRUIT_SIZE // 2, by)
            overlay(frame, r_img, int(self.right_x) - FRUIT_SIZE // 2, by)

    def slice(self):
        self.state = "cut"
        self.left_x = self.right_x = float(self.x)
        self.cut_y = float(self.y)
        self.cut_vy = self.vy
