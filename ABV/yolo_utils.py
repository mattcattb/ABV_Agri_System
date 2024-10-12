from ultralytics import YOLO
import os 
import json

valid_yolo_types = ['n', 's'] # nano and small are only supported types

def find_model(models_path, model_type):
    # Construct the expected model filename based on the model type
    if model_type == 'n':
        model_filename = 'yolo11n.pt'  # Name for YOLO 11 Nano
    elif model_type == 's':
        model_filename = 'yolo11s.pt'  # Name for YOLO 11 Small
    else:
        return None
    
    # Construct full path to the model file
    model_path = os.path.join(models_path, model_filename)
    
    # Check if the model file exists
    if not os.path.isfile(model_path):
        print(f"ERROR: Model file {model_filename} not found in {models_path}.")
        return None
    
    return model_path

def load_yolo(models_path, model_type='n'):
    if model_type not in valid_yolo_types:
        print("ERROR: Invalid YOLO Model Chosen!")
        return None
    
    # Find the correct model in the specified models path
    path_to_model = find_model(models_path, model_type)
    
    if path_to_model is None:
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
    print(f"img_name: {img_name}")
    base_name, _ = os.path.splitext(img_name)
    print(f"Base name: {base_name}")
    json_name = base_name + ".json"
    json_save_path = os.path.join(inf_folder, json_name)
    
    with open(json_save_path, 'w') as f:
        json.dump(json_result, f, indent=2)
        