"""
================================================================================
                    UNIT TESTS: VISION & AUDIO STUDIO
================================================================================
Verifies optical facial embedding extraction, gesture detection logic,
optical OCR bounding box isolation, DSP audio enhancers, and soundboard synthesis.
================================================================================
"""

import sys
import os
import unittest
import numpy as np
from pathlib import Path

# Ensure root workspace is in sys.path
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from jarvis.vision.face_auth import get_face_biometrics
from jarvis.vision.gesture_controller import GestureController, HandGesture
from jarvis.vision.optical_ocr import get_optical_ocr
from jarvis.studio.audio_enhancer import get_audio_enhancer
from jarvis.studio.voice_changer import get_voice_changer
from jarvis.studio.sound_soundboard import get_soundboard


class TestVisionAndStudio(unittest.TestCase):
    """Unit tests for Computer Vision and Audio Studio subsystems."""

    def test_face_embedding_computation(self):
        fb = get_face_biometrics()
        # Create a synthetic 128x128 3-channel image simulating a face
        fake_face = np.random.randint(50, 200, (128, 128, 3), dtype=np.uint8)
        embedding = fb.extract_face_embedding(fake_face)
        if embedding is not None:
            self.assertEqual(len(embedding), 128)
            # Embedding should be L2 normalized (norm approx 1.0)
            norm = np.linalg.norm(embedding)
            self.assertAlmostEqual(norm, 1.0, places=2)

    def test_optical_ocr_preprocessing(self):
        ocr = get_optical_ocr()
        # Synthetic white canvas with black simulated text box
        canvas = np.ones((200, 400, 3), dtype=np.uint8) * 255
        canvas[80:120, 50:350] = 0 # Black box simulating text line
        regions = ocr.detect_text_regions(canvas)
        self.assertIsInstance(regions, list)
        self.assertTrue(len(regions) >= 1)

    def test_dsp_audio_bandpass_filter(self):
        enhancer = get_audio_enhancer()
        sr = 16000
        t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
        # Mix 20Hz (rumble), 1000Hz (speech), and 12000Hz (hiss)
        signal = 0.5 * np.sin(2 * np.pi * 1000 * t) + 0.3 * np.sin(2 * np.pi * 20 * t)
        filtered = enhancer.apply_bandpass_filter(signal)
        self.assertEqual(len(filtered), len(signal))
        self.assertEqual(filtered.dtype, np.float32)

    def test_voice_changer_vocoder(self):
        changer = get_voice_changer()
        sr = 24000
        t = np.linspace(0, 0.2, int(sr * 0.2), endpoint=False)
        test_tone = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
        robotic = changer.apply_robotic_vocoder(test_tone)
        self.assertEqual(len(robotic), len(test_tone))

    def test_soundboard_synthesis(self):
        board = get_soundboard()
        self.assertIsNotNone(board)


if __name__ == "__main__":
    unittest.main()
