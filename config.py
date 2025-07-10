from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

QUALITY_STRICTNESS = os.getenv('QUALITY_STRICTNESS', 'medium').lower()

@dataclass
class QualityThresholds:
    """Configurable quality thresholds for different quality levels"""
    blur_threshold: float
    glare_threshold: float
    glare_brightness: int
    darkness_threshold: int
    min_contrast: float
    min_width: int
    min_height: int
    min_doc_area_ratio: float
    min_edge_density: float

# Easy (lenient)
easy_thresholds = QualityThresholds(
    blur_threshold=150.0,
    glare_threshold=0.01,
    glare_brightness=220,
    darkness_threshold=70,
    min_contrast=20.0,
    min_width=600,
    min_height=400,
    min_doc_area_ratio=0.2,
    min_edge_density=0.015
)

# Medium (your provided @dataclass default values)
medium_thresholds = QualityThresholds(
    blur_threshold=200.0,
    glare_threshold=0.005,
    glare_brightness=240,
    darkness_threshold=100,
    min_contrast=30.0,
    min_width=800,
    min_height=600,
    min_doc_area_ratio=0.3,
    min_edge_density=0.02
)

# Hard (strict)
hard_thresholds = QualityThresholds(
    blur_threshold=300.0,
    glare_threshold=0.003,
    glare_brightness=250,
    darkness_threshold=120,
    min_contrast=40.0,
    min_width=1000,
    min_height=800,
    min_doc_area_ratio=0.4,
    min_edge_density=0.025
)

if QUALITY_STRICTNESS == 'easy':
    thresholds = easy_thresholds
elif QUALITY_STRICTNESS == 'hard':
    thresholds = hard_thresholds
else:
    thresholds = medium_thresholds

instructions = """
Ensure good lighting without harsh shadows or glare
Hold camera steady and ensure the image is in focus 
Make sure the document fills most of the frame
Take photo straight-on to avoid perspective distortion
"""