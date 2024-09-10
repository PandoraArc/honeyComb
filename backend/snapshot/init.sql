CREATE TABLE session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_image_path VARCHAR(255) DEFAULT NULL,
    segmentation_path VARCHAR(255) DEFAULT NULL,
    classification_path VARCHAR(255) DEFAULT NULL,
    classification_data VARCHAR(255) DEFAULT NULL,
    transformation_path VARCHAR(255) DEFAULT NULL,
    transformation_data VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);