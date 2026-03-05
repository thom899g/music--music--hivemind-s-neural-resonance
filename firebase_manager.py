"""
Firebase State Management for Neural Resonance Ecosystem
Architectural Choice: Using Firestore for real-time state synchronization 
and persistence across distributed components.
"""
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from loguru import logger


class FirebaseManager:
    """Centralized state management for Neurosonic Ecosystem"""
    
    def __init__(self, service_account_path: str = None, project_id: str = None):
        """
        Initialize Firebase connection with robust error handling
        
        Args:
            service_account_path: Path to Firebase service account key
            project_id: Firebase project ID
        """
        self.service_account_path = service_account_path
        self.project_id = project_id
        self.db = None
        self._initialized = False
        
        # Initialize Firebase app
        self._initialize_firebase()
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK with multiple fallback strategies"""
        try:
            # Strategy 1: Use provided service account path
            if self.service_account_path and os.path.exists(self.service_account_path):
                cred = credentials.Certificate(self.service_account_path)
                app = firebase_admin.initialize_app(cred, {
                    'projectId': self.project_id or cred.project_id
                })
                logger.success(f"Firebase initialized with service account: {self.service_account_path}")
            
            # Strategy 2: Check environment variable
            elif 'FIREBASE_CREDENTIALS' in os.environ:
                env_path = os.environ['FIREBASE_CREDENTIALS']
                if os.path.exists(env_path):
                    cred = credentials.Certificate(env_path)
                    app = firebase_admin.initialize_app(cred)
                    logger.success(f"Firebase initialized from env variable: {env_path}")
                else:
                    raise FileNotFoundError(f"Service account file not found at: {env_path}")
            
            # Strategy 3: Use default application (