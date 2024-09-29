from nanocamera import Camera
import cv2

def test_single_save():
    cam = Camera()
    frame = cam.read()
    if frame is None:
        print("failed to print")
    else:
        cv2.imwrite("test_frame.jpg", frame)


def main():
    test_single_save()


if __name__ == "__main__":

	main()
