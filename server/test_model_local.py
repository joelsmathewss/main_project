import os
import sys

# Add parent directory to path to allow importing from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.model import MedicalDiagnosticSystem

def test_initialization():
    print("Testing MedicalDiagnosticSystem initialization...")
    # Pass a dummy API key or None
    system = MedicalDiagnosticSystem(groq_api_key="dummy_key")
    if system.model is None:
        print("Warning: Model not loaded. This is expected if the H5 file is missing.")
    else:
        print("Success: Model loaded.")
    
    print("Initialization test complete.")

if __name__ == "__main__":
    test_initialization()
