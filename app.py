from flask import Flask, jsonify
import cv2
import numpy as np
import threading

app = Flask(__name__)

# Definição das vagas para diferentes locais
locais = [
    {
        "nome": "Santa Maria",
        "latitude": -19.536347573976016,
        "longitude": -40.62884520237617,
        "vagas": [
            [1, 89, 108, 213], [115, 87, 152, 211], [289, 89, 138, 212], [439, 87, 135, 212],
            [591, 90, 132, 206], [738, 93, 139, 204], [881, 93, 138, 201], [1027, 94, 147, 202]
        ]
    },
    {
        "nome": "Avenida Central",
        "latitude": -19.540123,
        "longitude": -40.630456,
        "vagas": [
            [50, 100, 110, 220], [160, 100, 150, 220], [280, 100, 140, 220], [400, 100, 130, 220],
            [550, 100, 120, 220], [700, 100, 140, 220], [850, 100, 130, 220], [1000, 100, 145, 220]
        ]
    }
]

video = cv2.VideoCapture('video.mp4')

def exibir_video():
    while True:
        check, img = video.read()
        if not check:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        imgCinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgTh = cv2.adaptiveThreshold(imgCinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
        imgBlur = cv2.medianBlur(imgTh, 5)
        kernel = np.ones((3,3), np.uint8)
        imgDil = cv2.dilate(imgBlur, kernel)
        
        for local in locais:
            for x, y, w, h in local["vagas"]:
                recorte = imgDil[y:y+h, x:x+w]
                qtPxBranco = cv2.countNonZero(recorte)
                cor = (0, 0, 255) if qtPxBranco > 3000 else (0, 255, 0)
                cv2.rectangle(img, (x, y), (x + w, y + h), cor, 3)
        
        cv2.imshow('Video ao Vivo', img)
        cv2.imshow('Máscara Processada', imgDil)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

threading.Thread(target=exibir_video, daemon=True).start()

@app.route('/status_vagas', methods=['GET'])
def status_vagas():
    if not video.isOpened():
        return jsonify({"error": "Não foi possível abrir o vídeo"}), 500
    
    check, img = video.read()
    if not check:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        check, img = video.read()
    
    if not check:
        return jsonify({"error": "Não foi possível capturar frame do vídeo"}), 500
    
    imgCinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgTh = cv2.adaptiveThreshold(imgCinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    imgBlur = cv2.medianBlur(imgTh, 5)
    kernel = np.ones((3,3), np.uint8)
    imgDil = cv2.dilate(imgBlur, kernel)

    resposta = []
    
    for local in locais:
        status_vagas = {}
        for i, (x, y, w, h) in enumerate(local["vagas"], start=1):
            recorte = imgDil[y:y+h, x:x+w]
            qtPxBranco = cv2.countNonZero(recorte)
            status_vagas[f'vaga_{i}'] = 'Ocupada' if qtPxBranco > 3000 else 'Livre'
        
        # Adicionando informações do local
        status_vagas.update({
            "rua": local["nome"],
            "latitude": local["latitude"],
            "longitude": local["longitude"]
        })
        
        resposta.append(status_vagas)
    
    return jsonify(resposta)

if __name__ == '__main__':
    app.run(debug=True)
