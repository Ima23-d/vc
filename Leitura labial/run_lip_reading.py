import os
from lip_reading_system import LipReadingSystem

def simple_example():
    # Configurações - COLE SUA API KEY AQUI ↓
    API_KEY = "AIzaSyBwnowKJSq5x6qxhbbcnHz1qqe9NUVrZ0U"  # SUA API KEY REAL
    
    VIDEO_PATH = "videoplayback.mp4"  # Nome do seu arquivo de vídeo
    OUTPUT_FILE = "transcricao.txt"
    
    # Verifica se o vídeo existe
    if not os.path.exists(VIDEO_PATH):
        print(f"Vídeo {VIDEO_PATH} não encontrado!")
        print("Certifique-se de que o arquivo está na mesma pasta")
        return
    
    # Executa o sistema
    print("Iniciando análise de leitura labial...")
    system = LipReadingSystem(API_KEY)
    transcription = system.process_video(VIDEO_PATH, OUTPUT_FILE)
    
    return transcription

if __name__ == "__main__":
    simple_example()