import cv2

cap = cv2.VideoCapture(0)  # Change the index if necessary

if not cap.isOpened():
    print("Error: Could not open camera.")
else:
    print("Camera opened successfully!")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

cap.release()
cv2.destroyAllWindows()
