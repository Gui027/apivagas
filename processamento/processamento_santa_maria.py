import cv2
import numpy as np

def processar_frame(img, vagas):
    """Processa o frame e desenha os elementos do local Santa Maria corretamente."""
    img_processada = img.copy()  # Faz uma cópia da imagem original para não sobrescrever
    
    imgCinza = cv2.cvtColor(img_processada, cv2.COLOR_BGR2GRAY)
    imgTh = cv2.adaptiveThreshold(imgCinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    imgBlur = cv2.medianBlur(imgTh, 5)
    kernel = np.ones((3,3), np.uint8)
    imgDil = cv2.dilate(imgBlur, kernel)
    
    for x, y, w, h in vagas:
        recorte = imgDil[y:y+h, x:x+w]
        qtPxBranco = cv2.countNonZero(recorte)
        cor = (0, 0, 255) if qtPxBranco > 3000 else (0, 255, 0)
        cv2.rectangle(img_processada, (x, y), (x + w, y + h), cor, 3)  # Retângulo vermelho ou verde
    
    return img_processada, imgDil  # Retorna a imagem correta

