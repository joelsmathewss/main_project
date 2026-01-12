import os
import cv2
import json
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
from PIL import Image
from groq import Groq
from PyPDF2 import PdfReader

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YOLO_MODEL_PATH = os.path.join(BASE_DIR, 'last.pt')
CLASSIFIER_MODEL_PATH = os.path.join(BASE_DIR, 'densenet121_classifier_4_class_gpu.h5')
# Ensure data dir exists or handle its absence gracefully
CLASSIFIER_DATA_DIR = os.path.join(BASE_DIR, 'data', 'train') 

# Default Classes if directory not found
DEFAULT_CLASSES = ['covid-19', 'normal', 'pnemonia', 'tubercolosis']

class MedicalDiagnosticSystem:
    def __init__(self, api_key):
        self.api_key = api_key
        self.yolo_model = None
        self.classifier_model = None
        self.yolo_class_names = []
        self.classifier_class_names = []
        self._load_models()
        self.groq_client = Groq(api_key=api_key)

    def _load_models(self):
        try:
            print("⏳ Loading Vision Models...")
            if os.path.exists(YOLO_MODEL_PATH):
                self.yolo_model = YOLO(YOLO_MODEL_PATH)
                self.yolo_class_names = self.yolo_model.names
            else:
                print(f"⚠️ YOLO Model not found at {YOLO_MODEL_PATH}")

            if os.path.exists(CLASSIFIER_MODEL_PATH):
                self.classifier_model = tf.keras.models.load_model(CLASSIFIER_MODEL_PATH)
                if os.path.exists(CLASSIFIER_DATA_DIR):
                    self.classifier_class_names = sorted([d for d in os.listdir(CLASSIFIER_DATA_DIR) if os.path.isdir(os.path.join(CLASSIFIER_DATA_DIR, d))])
                    print(f"Loaded classifier classes: {self.classifier_class_names}")
                else:
                    print(f"⚠️ Data dir not found. Using default classes.")
                    self.classifier_class_names = DEFAULT_CLASSES
            else:
                print(f"⚠️ Classifier Model not found at {CLASSIFIER_MODEL_PATH}")
            
            print("✅ Models Loaded.")
        except Exception as e:
            print(f"❌ Error Loading Models: {e}")

    def analyze_image(self, image_path):
        if not self.yolo_model or not self.classifier_model:
            return {"error": "Models not loaded"}

        try:
            json_report = {
                "image_filename": os.path.basename(image_path),
                "overall_status": "Pending",
                "findings": []
            }

            original_image = cv2.imread(image_path)
            if original_image is None:
                return {"error": "Could not read image"}
            
            # Run YOLO
            results = self.yolo_model(original_image, imgsz=224, conf=0.1)
            CONF_THRESHOLD = 0.25

            if not results[0].boxes:
                json_report["overall_status"] = "Normal"
            else:
                high_conf_boxes = [b for b in results[0].boxes if b.conf[0] > CONF_THRESHOLD]

                if not high_conf_boxes:
                    json_report["overall_status"] = "Normal"
                else:
                    json_report["overall_status"] = "Abnormal"

                    for i, box in enumerate(high_conf_boxes):
                        xyxy = box.xyxy[0].int().tolist()
                        x1, y1, x2, y2 = xyxy
                        yolo_conf = float(box.conf[0].item())
                        
                        cls_id = int(box.cls[0].item())
                        # Safety check for class index
                        if 0 <= cls_id < len(self.yolo_class_names):
                            yolo_label = self.yolo_class_names[cls_id]
                        else:
                            yolo_label = "Unknown"

                        # Crop & Classify
                        cropped_image = original_image[y1:y2, x1:x2]
                        if cropped_image.size == 0:
                            continue

                        img_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                        img_resized = img_pil.resize((224, 224))
                        img_array = tf.keras.utils.img_to_array(img_resized) / 255.0
                        img_batch = np.expand_dims(img_array, axis=0)

                        preds = self.classifier_model.predict(img_batch, verbose=0)
                        class_score = float(np.max(preds[0]))
                        
                        pred_idx = np.argmax(preds[0])
                        if 0 <= pred_idx < len(self.classifier_class_names):
                            disease_name = self.classifier_class_names[pred_idx]
                        else:
                            disease_name = "Unknown"

                        json_report["findings"].append({
                            "finding_id": i + 1,
                            "classifier_prediction": disease_name,
                            "classifier_confidence": round(class_score * 100, 2),
                            "detector_object_type": yolo_label,
                            "detector_confidence": round(yolo_conf * 100, 2),
                            "bbox": [x1, y1, x2, y2]
                        })

            return json_report

        except Exception as e:
            return {"error": str(e)}

    def extract_pdf_text(self, pdf_path):
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return None

    def generate_summary(self, pdf_text, json_data, target_language="English"):
        try:
            json_string = json.dumps(json_data, indent=2) if json_data else "No X-ray analysis provided."
            
            # --- LANGUAGE PROMPT LOGIC ---
            if target_language == "ml": # 'ml' code for Malayalam from frontend
                lang_instruction = """
                OUTPUT LANGUAGE: MALAYALAM (മലയാളം).
                CRITICAL INSTRUCTION: DO NOT SHORTEN THE REPORT.
                - Provide a detailed and comprehensive explanation.
                - Explain why a value is dangerous (e.g., "ഓക്സിജൻ 88% ആയത് അപകടകരമാണ്, കാരണം...").
                - Use simple Malayalam words, but keep the explanation long and clear.
                - Translate every single finding from the English logic.
                """
            else:
                lang_instruction = """
                OUTPUT LANGUAGE: ENGLISH.
                - Provide a detailed layman explanation.
                - DEFINITIONS: Explain every medical term (e.g., "SpO2 (Oxygen Level)").
                - Connect all dots between Vitals and X-Ray.
                """

            system_instruction = f"""
            You are an expert doctor explaining a detailed diagnosis to a patient.

            STRICT FORMATTING RULES (Clean Text Only):
            1. NO Markdown (No #, **, -, etc).
            2. NO Emojis.
            3. NO Bullet points.
            4. Use simple "Title: Content" structure.

            REQUIRED SECTIONS:

            Vitals and Lab Data
            [Medical Term] ([Simple Explanation]): [Value] -> [Status/Risk]
            Example: SpO2 (Blood Oxygen Level): 88% -> Low (Hypoxia)
            (List each item on a new line)

            X-Ray Findings
            Condition: [Name]
            Location: [Location]
            Meaning: [Explanation]

            Integrated Summary
            [Write a detailed paragraph. State the main disease. Explain the evidence from X-ray and Lab data. Explain the link between them. Explain next steps.]

            {lang_instruction}
            """

            user_message = f"""
            Here is the raw data:

            --- SOURCE 1: AI X-RAY ANALYSIS ---
            {json_string}

            --- SOURCE 2: MEDICAL REPORT TEXT ---
            {pdf_text}

            Please generate the Detailed Integrated Summary in {target_language}.
            """

            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
            )

            return completion.choices[0].message.content

        except Exception as e:
            return f"❌ Groq API Error: {e}"

if __name__ == "__main__":
    # Local Test
    API_KEY = os.environ.get("GROQ_API_KEY")
    if API_KEY:
        system = MedicalDiagnosticSystem(API_KEY)
        print("Medical Diagnostic System Initialized.")
    else:
        print("Please set GROQ_API_KEY in environment variables.")