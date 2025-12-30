# tests/conftest.py
import pytest
from unittest.mock import MagicMock
import sys

# Mock modules before importing application code
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

# Set dummy env vars
import os
os.environ["GEMINI_API_KEY"] = "fake_key"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"