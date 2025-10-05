import os
import cv2
import numpy as np
import tensorflow as tf
import joblib
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename

# Blueprint setup
weed_bp = Blueprint('weed', __name__, url_prefix='/weed')

# Constants
UPLOAD_FOLDER = os.path.join('static', 'update')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Load models
try:
    model = tf.keras.models.load_model(r"C:\Users\pooja kumbhar\gui\models\model.h5")
    print("✅ Keras model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading Keras model: {e}")
    model = None

try:
    svm_model = joblib.load(r"C:\Users\pooja kumbhar\gui\models\svm_classifier.pkl")
    print("✅ SVM model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading SVM model: {e}")
    svm_model = None

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@weed_bp.route('/')
def home():
    user = {"name": "Pooja"}  # Replace with dynamic user info if using sessions
    return render_template('weed_index.html', user=user)

@weed_bp.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No file part"
    
    file = request.files['image']
    
    if file.filename == '':
        return "No selected file"
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            detection_results, output_image_relative_path = detection(filepath)
        except Exception as e:
            return f"Error in detection: {e}"

        user = {"name": "Pooja"}  # Again, use session user in real app
        return render_template('weed_result.html',
                               image_path=url_for('static', filename=output_image_relative_path),
                               detection_results=detection_results,
                               user=user)
    
    return redirect(url_for('weed.home'))

# Detection logic
def detection(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Error reading image")

    # Preprocess
    img_resized = cv2.resize(img, (224, 224))
    img_array = np.expand_dims(img_resized, axis=0) / 255.0
    predictions = model.predict(img_array)

    class_labels = ['weed', 'crop']
    predicted_class_id = np.argmax(predictions[0])
    predicted_class = class_labels[predicted_class_id % len(class_labels)]
    confidence = predictions[0][predicted_class_id] * 100

    # Draw bounding box
    color = (0, 255, 0) if predicted_class == 'crop' else (255, 0, 0)
    bbox_x, bbox_y, bbox_w, bbox_h = 30, 50, img.shape[1] - 60, img.shape[0] - 100
    cv2.rectangle(img, (bbox_x, bbox_y), (bbox_x + bbox_w, bbox_y + bbox_h), color, 2)
    label_text = f"{predicted_class} {confidence:.2f}%"
    cv2.putText(img, label_text, (bbox_x, bbox_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Save prediction output
    output_filename = f'prediction_{len(os.listdir(UPLOAD_FOLDER)) + 1}.jpg'
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    cv2.imwrite(output_path, img)

    return [(f"({bbox_x}, {bbox_y}, {bbox_w}, {bbox_h})", predicted_class, confidence)], f'update/{output_filename}'
