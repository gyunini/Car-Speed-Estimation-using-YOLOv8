import cv2

video_path = './video/video.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

ret, frame = cap.read()
if not ret:
    print("Error: Could not read the first frame.")
    cap.release()
    exit()

output_image_path = './img/first_frame.jpg'
cv2.imwrite(output_image_path, frame)