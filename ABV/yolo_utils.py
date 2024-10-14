from ultralytics import YOLO
import os 
import json

MODELS_DIR_PATH = "/home/preag/Desktop/ABV_Agri_System/ABV/yolo_models"

yolon_onnx = "yolo11n.onnx"
yolon = "yolo11n.pt"
yolos = "yolo11s.pt"

def find_model(models_path=MODELS_DIR_PATH, model_type="o"):
    # Construct the expected model filename based on the model type
    if model_type == "o":
        model_name = yolon_onnx
    elif model_type == "pt":
        model_name = yolon
    else:
        return None
    
    # Construct full path to the model file
    model_path = os.path.join(models_path, model_name)
    
    # Check if the model file exists
    if not os.path.isfile(model_path):
        print(f"ERROR: Model file {model_name} not found in {models_path}.")
        return None
    
    return model_path

def load_yolo(models_path=MODELS_DIR_PATH, model_type='o'):
    
    # Find the correct model in the specified models path
    path_to_model = find_model(models_path, model_type)
    
    if path_to_model is None:
        print(f"YOLO ERROR: no path to model of type{model_type}")
        return None  # Exit if the model path is not found
    
    # Load the model
    model = YOLO(path_to_model)

    return model


def save_results_json(results, inf_folder, img_name):
    """
        results: [Results] Ultralytics object
        inf_folder: Location of folder to store inferences 
        img_name: name of image being scanned
    """
    
    if len(results) != 1:
        print("ERROR: Too many results!")
        return None
    
    result = results[0]
    json_str_result = result.to_json(normalize=False)
    json_result = json.loads(json_str_result)
    base_name, _ = os.path.splitext(img_name)
    json_name = base_name + ".json"
    json_save_path = os.path.join(inf_folder, json_name)
    
    with open(json_save_path, 'w') as f:
        json.dump(json_result, f, indent=2)
        