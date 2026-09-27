# Project: Real-time Face Detection

## Summary
A small computer-vision application that detects faces in a live webcam stream using OpenCV's Haar Cascade classifier. It shows a mirrored view, draws a box around each face and displays the number of faces and the frames per second.
Code: https://github.com/khodiboev/computer_vision (face_detection_webcam.py)

## Results
Runs in real time at about 30 frames per second on a MacBook and detects multiple faces at once.

## Notes
- The script was moved out of a Colab notebook into a standalone Python program, because a notebook cannot use the laptop camera reliably.
- OpenCV 5 removed the Haar Cascade classifier, so the project pins OpenCV 4.x in requirements.txt.
- Face detection finds where a face is; it does not identify who the person is.

## Related work
As a research assistant at SMIT, Juno also assisted a professor on a face detection project and built small computer-vision applications as part of it.
