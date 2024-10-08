from ultralytics import YOLO

DEFAULT_MODEL_PATH = "/home/preag/Desktop/ABV_Agri_System/ABV/yolo_models/yolo11s.pt"

# Load a model
def get_model(model_path=DEFAULT_MODEL_PATH):
    """Load and return the YOLO model."""
    model = YOLO(model_path)  # Load the official YOLO model
    return model

def test_single_inference():
    """Test inference on a single image."""
    # Load the model
    model = get_model()  # You can specify a different path if needed

    # Define the path to the test image
    test_img = "/home/preag/Desktop/ABV_Agri_System/testing/test_img.png"
    
    # Predict with the model
    results = model(test_img)  # Run inference on the test image

    # Display results
    print("Inference Results:")
    print(results)

if __name__ == "__main__":
    test_single_inference()
