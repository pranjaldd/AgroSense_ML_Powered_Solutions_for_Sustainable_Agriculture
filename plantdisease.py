import os
import cv2
import numpy as np
from flask import Blueprint, render_template, request
from keras.models import load_model

plant_disease_bp = Blueprint('plant_bp', __name__, template_folder='templates')

DISEASE_MODEL_PATH = r"models/plant_disease_model.h5"
LEAF_MODEL_PATH = r"models/leaf_vs_nonleaf_model.h5"

disease_model = load_model(DISEASE_MODEL_PATH)
leaf_checker_model = load_model(LEAF_MODEL_PATH)

CATEGORIES = [
    'Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
    'Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight',
    'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot',
    'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot',
    'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus',
    'Tomato_healthy'
]

def prepare_image(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Could not read image.")
    img = cv2.resize(img, (100, 100))
    img = img / 255.0
    return img.reshape(-1, 100, 100, 3)

@plant_disease_bp.route('/plant_disease', methods=['GET', 'POST'])
def plant_disease():
    prediction = None
    error = None

    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file uploaded.'
        else:
            file = request.files['file']
            if file.filename == '':
                error = 'Please choose an image file.'
            else:
                upload_dir = os.path.join('static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                upload_path = os.path.join(upload_dir, file.filename)
                file.save(upload_path)

                try:
                    img = prepare_image(upload_path)
                    leaf_pred = leaf_checker_model.predict(img)[0][0]

                    if leaf_pred < 0.5:
                        prediction = "❌ This doesn't seem to be a leaf. Please upload a valid leaf image."
                    else:
                        pred = disease_model.predict(img)
                        result = CATEGORIES[pred.argmax()]
                        prediction = f"✅ Predicted Disease: {result}"
                except Exception as e:
                    error = f"Error: {str(e)}"

    return render_template('crophealth.html', prediction=prediction, error=error)
