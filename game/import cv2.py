import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
import random

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Game variables
bird_position_y = 250  # Initial vertical position of the bird
bird_velocity_y = 0  # Initial vertical speed (gravity effect removed)
score = 0  # Score initialization
highest_score = 0  # Highest score initialization
obstacles = []  # List to hold obstacles
game_running = False  # Flag to check if the game is running
game_over = False  # Flag to track if the game is over

# Initialize Tkinter window for the start button
def start_game():
    global game_running, game_over, score
    game_running = True
    game_over = False
    score = 0
    start_button.config(state="disabled")
    reset_game()
    game_loop()

# Initialize webcam
cap = cv2.VideoCapture(0)

# Create Tkinter window
root = tk.Tk()
root.title("Nose-Controlled Flappy Bird")

# Start button
start_button = tk.Button(root, text="Start Game", font=("Arial", 20), command=start_game)
start_button.pack(pady=20)

# Function to generate obstacles
def generate_obstacles():
    # Random height for the gap between obstacles
    gap = random.randint(150, 300)
    top_height = random.randint(50, 250)
    bottom_height = 600 - top_height - gap
    obstacles.append({'top': top_height, 'bottom': bottom_height, 'x': 600})

# Function to reset the game
def reset_game():
    global bird_position_y, bird_velocity_y, obstacles
    bird_position_y = 250
    bird_velocity_y = 0
    obstacles.clear()
    generate_obstacles()

# Game loop
def game_loop():
    global bird_position_y, bird_velocity_y, score, highest_score, obstacles, game_running, game_over
    previous_nose_y = 250  # Initialize with a default nose position

    while game_running:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a better user experience
        frame = cv2.flip(frame, 1)

        # Convert the frame to RGB (MediaPipe uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and get the face landmarks
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for landmarks in results.multi_face_landmarks:
                # Get the nose tip (landmark 1 in the MediaPipe FaceMesh model)
                nose_x = int(landmarks.landmark[1].x * frame.shape[1])
                nose_y = int(landmarks.landmark[1].y * frame.shape[0])

                # Adjust the sensitivity threshold for nodding (change 5 pixels)
                if nose_y < previous_nose_y - 5:  # Smaller upward nod
                    bird_position_y -= 10  # Smaller movement upwards
                elif nose_y > previous_nose_y + 5:  # Smaller downward nod
                    bird_position_y += 10  # Smaller movement downwards
                
                # Update the previous nose_y value
                previous_nose_y = nose_y

        # Keep the bird within bounds
        bird_position_y = max(50, min(bird_position_y, 450))

        # Move obstacles and check for collision
        for obstacle in obstacles:
            obstacle['x'] -= 3  # Slower movement of obstacles

            # Check for collision
            if (obstacle['x'] < 100 and obstacle['x'] + 50 > 50 and
                    (bird_position_y < obstacle['top'] or bird_position_y > obstacle['top'] + 150)):
                game_over = True
                highest_score = max(score, highest_score)

        # Remove obstacles that go out of the screen
        obstacles = [obstacle for obstacle in obstacles if obstacle['x'] > -50]

        # Generate new obstacles
        if not obstacles or obstacles[-1]['x'] < 300:
            generate_obstacles()

        # Update score
        score = len([obstacle for obstacle in obstacles if obstacle['x'] < 50])

        # Draw the bird (represented as a rectangle) on the frame
        cv2.rectangle(frame, (50, bird_position_y), 
                      (100, bird_position_y + 50), 
                      (0, 255, 0), -1)  # Green rectangle for bird

        # Draw obstacles (represented as two rectangles)
        for obstacle in obstacles:
            cv2.rectangle(frame, (obstacle['x'], 0), 
                          (obstacle['x'] + 50, obstacle['top']), 
                          (0, 0, 255), -1)  # Red rectangle for top obstacle
            cv2.rectangle(frame, (obstacle['x'], obstacle['top'] + 150), 
                          (obstacle['x'] + 50, 600), 
                          (0, 0, 255), -1)  # Red rectangle for bottom obstacle

        # Display score
        cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display highest score
        cv2.putText(frame, f"Highest Score: {highest_score}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display Game Over message
        if game_over:
            cv2.putText(frame, "Game Over!", (200, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow("Nose-Controlled Flappy Bird", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()

# Start the Tkinter main loop
root.mainloop()
