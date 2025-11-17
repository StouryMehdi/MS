import random
import pyautogui as pg
import time

animal =('cat', 'dog', 'lion', 'tiger', 'elephant', 'giraffe', 'zebra', 'bear', 'wolf', 'fox')
time.sleep(5)

for i in range(500):
   z=random.choice(animal)
   pg.write("You are a"+z)
   pg.press("enter")