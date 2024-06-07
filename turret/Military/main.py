import depthai as dai
import cv2
import numpy as np
import serial
import time

# Serial communication with Arduino
ser = serial.Serial('COM4', 9600)

# Start defining a pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
camRgb = pipeline.createColorCamera()
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)


# Define a source - depth camera
camDepth = pipeline.createMonoCamera()
camDepth.setBoardSocket(dai.CameraBoardSocket.LEFT)

# Create output
xoutRgb = pipeline.createXLinkOut()
xoutRgb.setStreamName("rgb")
camRgb.video.link(xoutRgb.input)

xoutDepth = pipeline.createXLinkOut()
xoutDepth.setStreamName("depth")
camDepth.out.link(xoutDepth.input)

# Create a device
with dai.Device(pipeline) as device:
    # Start pipeline
    device.startPipeline()

    # Output queues will be used to get the rgb and depth frames
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    qDepth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

    # Create a resizable window
    cv2.namedWindow("Multiple Color Detection in Real-Time", cv2.WINDOW_NORMAL)

    red_in_box = False  # Flag to indicate if the red object is in the white box


    while True:
        inRgb = qRgb.get()  # Blocking call, will wait until a new data has arrived
        inDepth = qDepth.get()

        # Get BGR frame from Oak-D camera
        frame = inRgb.getCvFrame()
        depthFrame = inDepth.getFrame()


        prev_frame = frame.copy()

        # Get the dimensions of the frame
        frame_height, frame_width = frame.shape[:2]

        # Convert BGR frame to HSV
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define color ranges
        colors = {
            "red": ((0, 0, 255), [136, 87, 111], [180, 255, 255]),
        }

        max_area = 0
        max_area_bbox = None

        # Loop over each color, create mask, and detect objects
        for color_name, (color, lower, upper) in colors.items():
            # Create mask
            mask = cv2.inRange(hsvFrame, np.array(lower), np.array(upper))

            # Morphological Transform, Dilation
            kernel = np.ones((5, 5), "uint8")
            mask = cv2.dilate(mask, kernel)

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Loop over detected contours
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 200:
                    if area > max_area:
                        max_area = area
                        max_area_bbox = cv2.boundingRect(contour)

        if max_area_bbox is not None:
            x, y, w, h = max_area_bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), colors["red"][0], 2)
            cv2.putText(frame, "Largest Red", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, colors["red"][0])

            # Draw a dot at the center of the bounding box
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.circle(frame, (center_x, center_y), 5, colors["red"][0], -1)

            # Create a white box in the center of the frame (hollow)
            white_box_size = 50
            white_box_thickness = 2
            white_box_x = (frame_width - white_box_size) // 2
            white_box_y = ((frame_height - white_box_size) // 2) + 0
            cv2.rectangle(frame, (white_box_x, white_box_y), (white_box_x + white_box_size, white_box_y + white_box_size), (255, 255, 255), white_box_thickness)

            # Send commands to Arduino based on relative positions
            if center_y < white_box_y:
                message = "U"
                ser.write(message.encode())
                print(message)
                time.sleep(0.09)
            elif center_y > white_box_y + white_box_size:
                message = "D"
                ser.write(message.encode())
                print(message)
                time.sleep(0.09)
            if center_x < white_box_x:
                message = "R"
                ser.write(message.encode())
                print(message)
                time.sleep(0.09)
            elif center_x > white_box_x + white_box_size:
                message = "L"
                ser.write(message.encode())
                print(message)
                time.sleep(0.09)

            # Check if the red object is in the white box
            if white_box_x <= center_x <= white_box_x + white_box_size and white_box_y <= center_y <= white_box_y + white_box_size:
                if not red_in_box:
                    ser.write(b'S')  # Send 'S' command to Arduino once when red object enters the white box
                    red_in_box = True
            else:
                red_in_box = False

            # Calculate depth of the red object if within the depth frame bounds
            if 0 <= int(center_y) < depthFrame.shape[0] and 0 <= int(center_x) < depthFrame.shape[1]:
                depth = depthFrame[int(center_y), int(center_x)] / 1000.0  # Convert depth from millimeters to meters

                # Display distance above the bounding box
                cv2.putText(frame, f"Depth: {depth:.2f} m", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, colors["red"][0])

        # Show frame with detected colors
        cv2.imshow("Multiple Color Detection in Real-Time", frame)

        # Exit if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup   
cv2.destroyAllWindows()
