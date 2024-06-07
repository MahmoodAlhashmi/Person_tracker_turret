Person Tracker Turret

An autonomous turret that uses person recognition to aim at a person and then shoot yellow foam balls at them. It can also be controlled using a PS4 controller connected to a laptop. The code is located in the turret directory.
Components Needed

    1 Oak-D camera 
    2 brushless motors
    2 ESCs (Electronic Speed Controllers)
    1 Arduino Nano
    1 battery (an 11.7V battery supply was used in this project)

Arduino Nano Connections

    servo_x (X-axis servo) ---> Pin 11
    servo_y (Y-axis servo) ---> Pin 10
    servo_f (shooting servo) ---> Pin 9
    ESC1 (right brushless motor) ---> Pin 6
    ESC2 (left brushless motor) ---> Pin 5

Controlling the Turret with a PS4 Controller

    Connect the PS4 controller to your PC using Bluetooth.
    Run the controller_inputs.py file.
    Use the joystick to move the turret up, down, left, and right. Press X to shoot.

Person Tracking

To enable person tracking, run the main.py file located in the military folder.
