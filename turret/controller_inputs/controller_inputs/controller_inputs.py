import pygame
import sys
from pygame.locals import *
import serial

ser = serial.Serial('COM4', 9600)

pygame.init()
pygame.display.set_caption("game base")
screen = pygame.display.set_mode((500, 500), 0, 32)
clock = pygame.time.Clock()

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

my_square = pygame.Rect(50, 50, 50, 50)

my_square_color = 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
motion = [0, 0]

# Initialize variables to keep track of the time when each command is sent
last_U_time = 0
last_D_time = 0
last_L_time = 0
last_R_time = 0

# Define the delay time in milliseconds
delay_time = 10  # Adjust this value as needed

while True:

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, colors[my_square_color], my_square)
    my_square.x += motion[0] * 10
    my_square.y += motion[1] * 10

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():

        if event.type == JOYBUTTONDOWN:
            print(event)
            if event.button == 0:
                message = "S"
                ser.write(message.encode())
                print(message)

        if event.type == JOYAXISMOTION:
            print(event)
            if event.axis == 0:
                motion[0] = event.value
                if event.value > 0.2 and current_time - last_L_time >= delay_time:
                    message = "L"
                    ser.write(message.encode())
                    #print(message)
                    last_L_time = current_time
                elif event.value < -0.2 and current_time - last_R_time >= delay_time:
                    message = "R"
                    ser.write(message.encode())
                    #print(message)
                    last_R_time = current_time

            if event.axis == 1:
                motion[1] = event.value
                if event.value > 0.2 and current_time - last_D_time >= delay_time:
                    message = "D"
                    ser.write(message.encode())
                    #print(message)
                    last_D_time = current_time
                if event.value < -0.2 and current_time - last_U_time >= delay_time:
                    message = "U"
                    ser.write(message.encode())
                    #print(message)
                    last_U_time = current_time

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    pygame.display.update()
    clock.tick(60)
