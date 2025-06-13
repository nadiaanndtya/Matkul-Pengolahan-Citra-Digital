import cv2
import numpy as np
from matplotlib import pyplot as plt

def to_grayscale(img):
    if img is None:
        return None
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def to_binary(img, threshold=127):
    gray = to_grayscale(img)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary

def arithmetic_add(img1, img2):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return cv2.add(img1, img2)

def logic_and(img1, img2):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return cv2.bitwise_and(img1, img2)

def to_binary(img, threshold=127):
    if img is None:
        return None
    gray = to_grayscale(img)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary

def apply_filter(img, mode='edge'):
    if img is None:
        return None
    
    gray = to_grayscale(img)

    if mode == 'edge':
        # Gunakan Canny edge detection
        edges = cv2.Canny(gray, threshold1=50, threshold2=150)
        return edges
    else:
        raise ValueError("Unsupported filter mode. Only 'edge' is implemented.")
    
def show_histogram(img):
    plt.figure()
    if len(img.shape) == 2:
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        plt.plot(hist, color='gray')
    else:
        color = ('b', 'g', 'r')
        for i, col in enumerate(color):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)

    plt.title('Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()
    return True  # Tambahan opsional

def morphology(img):
    binary = to_binary(img)

    # Gunakan structuring element yang lebih besar (misal 7x7)
    se1 = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))  # Full Square
    se2 = cv2.getStructuringElement(cv2.MORPH_CROSS, (15, 15))  # Silang

    # Terapkan dilasi
    result1 = cv2.dilate(binary, se1, iterations=1)
    result2 = cv2.dilate(binary, se2, iterations=1)

    return result1, result2
