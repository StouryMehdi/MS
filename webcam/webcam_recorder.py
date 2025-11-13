import cv2
import sys
import datetime
import platform # Added for OS checking

# --- Configuration for Recording ---
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAME_RATE = 30.0

# Choose codec based on OS for maximum compatibility
if platform.system() == "Windows":
    FOURCC = cv2.VideoWriter_fourcc(*'XVID') 
    print("[*] Using XVID codec (Windows compatible).")
elif platform.system() == "Linux":
    FOURCC = cv2.VideoWriter_fourcc(*'MJPG')
    print("[*] Using MJPG codec (Linux compatible).")
else:
    FOURCC = cv2.VideoWriter_fourcc(*'XVID')
    print("[*] Using default XVID codec.")


# Create a unique filename with a timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"webcam_recording_{timestamp}.avi" 
# -----------------------------------

# Initialize camera capture (0 is usually the default webcam)
cap = cv2.VideoCapture(0)

# Set the resolution for the capture device
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)


if not cap.isOpened():
    print("Error: Could not open webcam. Check permissions and device ID.")
    sys.exit(1)

# Initialize VideoWriter object
out = cv2.VideoWriter(output_filename, FOURCC, FRAME_RATE, (FRAME_WIDTH, FRAME_HEIGHT))
if not out.isOpened():
    print("Error: Could not open VideoWriter. Check codec or file path.")
    cap.release()
    sys.exit(1)


print(f"Recording started in background. Saving to: {output_filename}")
print("Press Ctrl+C to stop the recording and exit.")

try:
    # --- Main Video Loop ---
    while True:
        # Read a frame from the camera.
        success, frame = cap.read()
        
        if not success:
            print("Error: Failed to read frame.")
            break

        # Check if the frame size matches the VideoWriter settings
        if frame.shape[1] != FRAME_WIDTH or frame.shape[0] != FRAME_HEIGHT:
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        # --- WRITE FRAME TO FILE (The recording action) ---
        out.write(frame)

except KeyboardInterrupt:
    print("\nProgram interrupted by user (Ctrl+C). Stopping recording...")
    
finally:
    print("Releasing VideoWriter...")
    out.release()
    print("Releasing Camera...")
    cap.release()
    cv2.destroyAllWindows() 
    sys.exit(0)