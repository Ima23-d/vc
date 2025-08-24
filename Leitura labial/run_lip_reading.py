import os
from lip_reading_system import LipReadingSystem

def simple_example():
    # Configurações
    API_KEY = "AIzaSyBwnowKJSq5x6qxhbbcnHz1qqe9NUVrZ0U"  # Substitua pela sua API key
    VIDEO_PATH = "seu_video.mp4"  # Caminho para seu vídeo
    OUTPUT_FILE = "transcricao.txt"
    
    # Verifica se a API key foi configurada
    if API_KEY == "AIzaSyBwnowKJSq5x6qxhbbcnHz1qqe9NUVrZ0U":
        print("Por favor, configure sua API key do Gemini!")
        print("Obtenha uma em: https://aistudio.google.com/app/apikey")
        return
    
    # Verifica se o vídeo existe
    if not os.path.exists(VIDEO_PATH):
        print(f"Vídeo {VIDEO_PATH} não encontrado!")
        return
    
    # Executa o sistema
    system = LipReadingSystem(API_KEY)
    transcription = system.process_video(VIDEO_PATH, OUTPUT_FILE)
    
    return transcription

if __name__ == "__main__":
    simple_example()