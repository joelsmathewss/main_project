import os
import cv2
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from groq import Groq
from PyPDF2 import PdfReader

# Constants
MODEL_FILENAME = 'densenet121_classifier_4_class_gpu.h5'
LAST_CONV_LAYER = 'conv5_block16_2_conv'
CLASS_NAMES = ['COVID-19', 'Normal', 'Pneumonia', 'Tuberculosis']

class MedicalDiagnosticSystem:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.model = self._load_model()
        self.groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

    def _load_model(self):
        """Loads the DenseNet model from the local directory."""
        # Assuming the model file is in the same directory as this script or the server root
        # Try finding it relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, MODEL_FILENAME)
        
        # If not found, try going up one level (server root)
        if not os.path.exists(model_path):
             model_path = os.path.join(os.path.dirname(current_dir), MODEL_FILENAME)

        if os.path.exists(model_path):
            try:
                print(f"Loading model from {model_path}...")
                model = load_model(model_path)
                print("Model loaded successfully.")
                return model
            except Exception as e:
                print(f"Error loading model: {e}")
                return None
        else:
            print(f"Model file {MODEL_FILENAME} not found.")
            return None

    def extract_pdf_text(self, pdf_path):
        """Reads text from the uploaded PDF."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    def _get_gradcam_data(self, img_tensor, original_img):
        """Generates the heatmap, finds the hotspot, and determines the location string."""
        try:
            grad_model = Model(
                inputs=self.model.inputs,
                outputs=[self.model.get_layer(LAST_CONV_LAYER).output, self.model.output]
            )

            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(img_tensor)
                pred_index = tf.argmax(predictions[0])
                loss = predictions[:, pred_index]

            grads = tape.gradient(loss, conv_outputs)
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
            heatmap = conv_outputs[0] @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)
            heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
            heatmap = heatmap.numpy()

            heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
            
            # Find Hotspot
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(heatmap_resized)
            hotspot_x, hotspot_y = max_loc

            # Determine Location String
            width = original_img.shape[1]
            height = original_img.shape[0]

            side = "Right Lung" if hotspot_x < width / 2 else "Left Lung"
            
            if hotspot_y < height / 3: zone = "Upper Zone"
            elif hotspot_y < (2 * height) / 3: zone = "Middle Zone"
            else: zone = "Lower Zone"

            return f"{side} ({zone})"

        except Exception as e:
            print(f"Grad-CAM Error: {e}")
            return "Chest Area"

    def analyze_image(self, image_path):
        """Analyzes an X-ray image and returns the findings."""
        if self.model is None:
            return {"error": "Model not loaded"}

        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Could not read image"}

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, (224, 224))
            img_tensor = np.expand_dims(img_resized / 255.0, axis=0)

            # Predict
            preds = self.model.predict(img_tensor, verbose=0)
            class_idx = np.argmax(preds[0])
            confidence = float(np.max(preds[0]))
            disease_name = CLASS_NAMES[class_idx]

            # Grad-CAM Location
            location = self._get_gradcam_data(img_tensor, img)

            json_report = {
                "overall_status": "Abnormal" if disease_name != "Normal" else "Normal",
                "findings": []
            }

            if disease_name != "Normal":
                json_report["findings"].append({
                    "condition": disease_name,
                    "confidence": f"{confidence*100:.1f}%",
                    "location": location,
                    "note": "AI detected anomaly using Grad-CAM attention."
                })
            else:
                 json_report["findings"].append({
                    "condition": "Normal",
                    "confidence": f"{confidence*100:.1f}%",
                    "location": "N/A"
                })
            
            return json_report

        except Exception as e:
            print(f"Image Analysis Error: {e}")
            return {"error": str(e)}

    def generate_summary(self, pdf_text, image_findings, target_language="English"):
        """Generates a detailed summary using Groq."""
        if not self.groq_client:
            return "Groq Client not initialized. Check API Key."

        try:
            json_string = json.dumps(image_findings, indent=2) if image_findings else "No X-ray analysis provided."
            pdf_content = pdf_text if pdf_text else "No Medical Report Text provided."

            if target_language == "ml" or target_language == "Malayalam":
                lang_instruction = """
                OUTPUT LANGUAGE: MALAYALAM.
                CRITICAL INSTRUCTION: DO NOT SHORTEN THE REPORT.
                Provide a detailed and comprehensive explanation, same length as English.
                Explain why a value is dangerous.
                Use simple Malayalam words, but keep the explanation long and clear.
                Translate every single finding from the English logic.
                """
            else:
                lang_instruction = """
                OUTPUT LANGUAGE: ENGLISH.
                - Provide a detailed layman explanation.
                - Connect all dots between Vitals and X-Ray.
                """

            system_instruction = f"""
            You are an expert doctor explaining a detailed diagnosis to a patient.

            STRICT FORMATTING RULES:
            1. PLAIN TEXT ONLY. Do not use markdown (no bold **, no headers #, no bullets -).
            2. NO Emojis.
            3. NO Numbered lists for sections.
            4. Format exactly like the examples below.

            REQUIRED OUTPUT FORMAT:

            Vitals and Lab Data
            [Medical Term] ([Simple Definition]): [Value] -> [Status]
            [Medical Term] ([Simple Definition]): [Value] -> [Status]

            X-Ray Findings
            Condition: [Name]
            Location: [Location]
            Meaning: [Explanation]

            Integrated Summary
            [Detailed paragraph explaining the condition, evidence, and next steps in simple language.]

            {lang_instruction}
            """

            user_message = f"""
            Here is the raw data:

            --- SOURCE 1: AI X-RAY ANALYSIS (DenseNet + GradCAM) ---
            {json_string}

            --- SOURCE 2: MEDICAL REPORT TEXT ---
            {pdf_content}

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
            return f"Groq API Error: {e}"