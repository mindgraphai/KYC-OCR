from typing import Tuple, Optional
import cv2
import numpy as np
from dotenv import load_dotenv

def is_blurry(img: np.ndarray, threshold: float = 100.0) -> Tuple[bool, float]:
    """
    Check if an image is blurry using Laplacian variance.
    
    Args:
        img: Input image as numpy array
        threshold: Blur threshold (lower = more strict)
        
    Returns:
        Tuple of (is_blurry, variance_value)
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold #, variance


def has_glare(img: np.ndarray, threshold: float = 0.01, bright_threshold: int = 220) -> Tuple[bool, float]:
    """
    Check if an image has glare by detecting very bright pixels.
    
    Args:
        img: Input image as numpy array
        threshold: Percentage threshold for glare detection
        bright_threshold: Brightness threshold for pixel classification
        
    Returns:
        Tuple of (has_glare, glare_ratio)
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bright_mask = cv2.threshold(gray, bright_threshold, 255, cv2.THRESH_BINARY)
    glare_ratio = np.sum(bright_mask == 255) / (img.shape[0] * img.shape[1])
    return glare_ratio > threshold #, glare_ratio


def is_dark(img: np.ndarray, threshold: int = 80) -> Tuple[bool, float]:
    """
    Check if an image is too dark.
    
    Args:
        img: Input image as numpy array
        threshold: Mean brightness threshold
        
    Returns:
        Tuple of (is_dark, mean_brightness)
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(np.mean(gray))
    return mean_brightness < threshold #, mean_brightness

def has_contours(img: np.ndarray) -> Optional[np.ndarray]:
    """
    Find the largest 4-point contour representing a document outline.
    
    Args:
        img: Input image as numpy array
        
    Returns:
        Document contour points or None if not found
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and check for 4-point approximation
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:
            return approx
    return None

def deskew_image(img: np.ndarray, contour: np.ndarray) -> np.ndarray:
    """
    Deskew a document to a top-down view using perspective transform.
    
    Args:
        img: Input image as numpy array
        contour: 4-point document contour
        
    Returns:
        Deskewed image
    """
    # Reshape contour to 4x2 array
    points = contour.reshape(4, 2).astype("float32")
    
    # Sort points: top-left, top-right, bottom-right, bottom-left
    sum_coords = points.sum(axis=1)
    diff_coords = np.diff(points, axis=1)
    
    rect = np.array([
        points[np.argmin(sum_coords)],      # top-left
        points[np.argmin(diff_coords)],     # top-right
        points[np.argmax(sum_coords)],      # bottom-right
        points[np.argmax(diff_coords)]      # bottom-left
    ])
    
    # Calculate dimensions
    width = int(max(
        np.linalg.norm(rect[2] - rect[3]),  # bottom-right to bottom-left
        np.linalg.norm(rect[1] - rect[0])   # top-right to top-left
    ))
    height = int(max(
        np.linalg.norm(rect[1] - rect[2]),  # top-right to bottom-right
        np.linalg.norm(rect[0] - rect[3])   # top-left to bottom-left
    ))
    
    # Define destination rectangle
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")
    
    # Apply perspective transform
    transform_matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(img, transform_matrix, (width, height))


def image_preops(image_path: str):
    image_object = cv2.imread(image_path)
    if image_object is not None:
        if not is_blurry(image_object):
            if not has_glare(image_object):
                if not is_dark(image_object):
                    contour = has_contours(image_object)
                    if contour is not None:
                        deskewed = deskew_image(image_object, contour)
                        success, jpg_bytes = cv2.imencode('.jpg', deskewed)
                        if success:
                            return (jpg_bytes.tobytes(), "")
                        else:
                            return (None, "Failed to encode image as JPEG!")
                    return (None, "No Edges Found!")
                return (None, "Image Too Dark!")
            return (None, "Image too Bright!")
        return (None, "Image too Blurry!")
    return (None, "Cannot read image!")
