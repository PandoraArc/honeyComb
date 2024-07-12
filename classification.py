import os
import sys
from decimer_image_classifier import DecimerImageClassifier

def main(image_path):
    # Check if the provided path is a file
    if not os.path.isfile(image_path):
        print(f"Error: The path {image_path} does not exist or is not a file.")
        return

    # Instantiate DecimerImageClassifier (this loads the model and all needed settings)
    decimer_classifier = DecimerImageClassifier()

    # If you just need a statement about the image at image_path being a chemical structure or not:
    result = decimer_classifier.is_chemical_structure(image_path)
    print(result)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    main(image_path)
