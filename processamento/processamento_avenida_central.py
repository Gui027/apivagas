import cv2
import numpy as np

def processar_frame(img, vagas):
    """Processa o frame e desenha os elementos do local Avenida Central."""
    imgCinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgTh = cv2.adaptiveThreshold(imgCinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 15)
    imgBlur = cv2.medianBlur(imgTh, 7)
    kernel = np.ones((5,5), np.uint8)
    imgDil = cv2.dilate(imgBlur, kernel)
    
    for x, y, w, h in vagas:
        recorte = imgDil[y:y+h, x:x+w]
        qtPxBranco = cv2.countNonZero(recorte)
        cor = (255, 0, 0) if qtPxBranco > 2500 else (0, 255, 255)  # Azul se ocupado, amarelo se livre
        cv2.circle(img, (x + w//2, y + h//2), 15, cor, -1)  # Círculo no centro
    
    return img, imgDil
