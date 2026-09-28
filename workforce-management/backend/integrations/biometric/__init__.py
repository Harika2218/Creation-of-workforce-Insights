"""
Biometric Integrations Package
"""
from backend.integrations.biometric.biometric_connector import BiometricDeviceConnector
from backend.integrations.biometric.face_recognition import FaceRecognitionValidator

__all__ = ["BiometricDeviceConnector", "FaceRecognitionValidator"]
