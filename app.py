from flask import Flask, jsonify
import cv2
import numpy as np
import threading
import importlib
from locais.lista_locais import locais  # Importando locais

app = Flask(__name__)

# Dicionário para armazenar os vídeos e processamentos por local
videos = {}
processadores = {}

# Inicializar vídeos e carregar dinamicamente os módulos de processamento
for local in locais:
    videos[local["nome"]] = cv2.VideoCapture(local["video"])
    
    # Importa dinamicamente o módulo de processamento do local
    nome_modulo = f'processamento.processamento_{local["nome"].lower().replace(" ", "_")}'
    try:
        processadores[local["nome"]] = importlib.import_module(nome_modulo).processar_frame
    except ModuleNotFoundError:
        print(f"⚠️ Módulo de processamento não encontrado para {local['nome']}, usando default.")
        processadores[local["nome"]] = lambda img, vagas: (img, img)  # Função padrão caso não tenha um processamento específico

def exibir_video(local):
    video = videos[local["nome"]]
    processar_frame = processadores[local["nome"]]

    while True:
        check, img = video.read()
        if not check:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        img, imgDil = processar_frame(img, local["vagas"])  # Chama a função específica do local
        
        cv2.imshow(f'Video ao Vivo - {local["nome"]}', img)
        cv2.imshow(f'Máscara Processada - {local["nome"]}', imgDil)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

# Criando uma thread separada para cada local
for local in locais:
    threading.Thread(target=exibir_video, args=(local,), daemon=True).start()

@app.route('/status_vagas', methods=['GET'])
def status_vagas():
    resposta = []
    
    for local in locais:
        video = videos[local["nome"]]
        processar_frame = processadores[local["nome"]]

        if not video.isOpened():
            return jsonify({"error": f"Não foi possível abrir o vídeo de {local['nome']}"}), 500
        
        check, img = video.read()
        if not check:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            check, img = video.read()
        
        if not check:
            return jsonify({"error": f"Não foi possível capturar frame do vídeo de {local['nome']}"}), 500
        
        img, imgDil = processar_frame(img, local["vagas"])  # Chama o processamento específico do local

        status_vagas = {}
        for i, (x, y, w, h) in enumerate(local["vagas"], start=1):
            recorte = imgDil[y:y+h, x:x+w]
            
            # Converter para escala de cinza se necessário
            if len(recorte.shape) == 3:
                recorte = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
            
            qtPxBranco = cv2.countNonZero(recorte)
            status_vagas[f'vaga_{i}'] = 'Ocupada' if qtPxBranco > 3000 else 'Livre'
        
        status_vagas.update({
            "rua": local["nome"],
            "latitude": local["latitude"],
            "longitude": local["longitude"]
        })
        
        resposta.append(status_vagas)
    
    return jsonify(resposta)

if __name__ == '__main__':
    app.run(debug=True)
