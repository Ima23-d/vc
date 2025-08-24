import cv2
import numpy as np
import google.generativeai as genai  # Correto: google.generativeai
import tempfile
import os
from moviepy.editor import VideoFileClip  # Correto: moviepy.editor
import base64
import time
from PIL import Image
import argparse
class LipReadingSystem:
    def __init__(self, api_key):
        """
        Inicializa o sistema de leitura labial
        """
        self.api_key = api_key
        self.setup_gemini()
        
    def setup_gemini(self):
        """Configura a API do Gemini"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def extract_frames(self, video_path, frame_interval=10):
        """
        Extrai frames do vídeo em intervalos regulares
        """
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                # Converte BGR para RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
                
            frame_count += 1
            
        cap.release()
        return frames
    
    def detect_face_region(self, frame):
        """
        Detecta a região do rosto e boca no frame
        """
        # Carrega o classificador Haar para detecção facial
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            x, y, w, h = faces[0]
            # Define a região da boca (parte inferior do rosto)
            mouth_region = (x, y + h//2, w, h//2)
            return mouth_region
        return None
    
    def crop_mouth_region(self, frame, region):
        """
        Recorta a região da boca do frame
        """
        if region is None:
            return frame
            
        x, y, w, h = region
        cropped = frame[y:y+h, x:x+w]
        return cropped
    
    def frames_to_base64(self, frames):
        """
        Converte frames para base64
        """
        base64_frames = []
        for frame in frames:
            # Redimensiona o frame para melhor performance
            img = Image.fromarray(frame)
            img = img.resize((320, 240))  # Reduz resolução
            buffered = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(buffered, format="JPEG", quality=85)
            buffered.close()
            
            with open(buffered.name, "rb") as f:
                base64_frames.append(base64.b64encode(f.read()).decode('utf-8'))
            os.unlink(buffered.name)
            
        return base64_frames
    
    def analyze_lip_movement(self, base64_frames):
        """
        Analisa o movimento labial usando o Gemini
        """
        prompt = """
        Analise esta sequência de frames mostrando o movimento labial de uma pessoa.
        Baseado apenas no movimento dos lábios, transcreva o que a pessoa está dizendo.
        Considere a sequência temporal dos movimentos.
        
        Responda APENAS com a transcrição do que foi dito, sem comentários adicionais.
        Se não for possível determinar, responda: "Não foi possível transcrever".
        """
        
        # Prepara as imagens para o Gemini
        image_parts = []
        for img_data in base64_frames:
            image_parts.append({
                "mime_type": "image/jpeg",
                "data": img_data
            })
        
        try:
            response = self.model.generate_content([prompt] + image_parts)
            return response.text
        except Exception as e:
            print(f"Erro na análise: {e}")
            return "Erro na transcrição"
    
    def process_video(self, video_path, output_text_file=None):
        """
        Processa o vídeo completo e faz a transcrição
        """
        print("Extraindo frames do vídeo...")
        frames = self.extract_frames(video_path, frame_interval=8)
        
        if not frames:
            print("Nenhum frame extraído do vídeo.")
            return
        
        print(f"Extraídos {len(frames)} frames.")
        print("Processando regiões da boca...")
        
        # Processa cada frame para focar na região da boca
        mouth_frames = []
        for frame in frames:
            mouth_region = self.detect_face_region(frame)
            if mouth_region:
                mouth_frame = self.crop_mouth_region(frame, mouth_region)
                mouth_frames.append(mouth_frame)
            else:
                mouth_frames.append(frame)  # Usa frame completo se não detectar rosto
        
        print("Convertendo frames para base64...")
        base64_frames = self.frames_to_base64(mouth_frames)
        
        print("Analisando movimento labial com Gemini...")
        transcription = self.analyze_lip_movement(base64_frames)
        
        print("\n" + "="*50)
        print("TRANSCRIÇÃO COMPLETA:")
        print("="*50)
        print(transcription)
        print("="*50)
        
        if output_text_file:
            with open(output_text_file, 'w', encoding='utf-8') as f:
                f.write(transcription)
            print(f"Transcrição salva em: {output_text_file}")
        
        return transcription

def main():
    parser = argparse.ArgumentParser(description='Sistema de Leitura Labial com Gemini')
    parser.add_argument('video_path', help='Caminho para o vídeo de entrada')
    parser.add_argument('--api-key', required=True, help='Sua API Key do Google Gemini')
    parser.add_argument('--output', help='Arquivo de saída para a transcrição')
    
    args = parser.parse_args()
    
    # Verifica se o arquivo de vídeo existe
    if not os.path.exists(args.video_path):
        print(f"Erro: Arquivo {args.video_path} não encontrado!")
        return
    
    # Inicializa o sistema
    system = LipReadingSystem(args.api_key)
    
    # Processa o vídeo
    system.process_video(args.video_path, args.output)

if __name__ == "__main__":
    main()