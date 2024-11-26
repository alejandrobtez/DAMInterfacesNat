import webbrowser
import speech_recognition as sr
import subprocess 
 
r = sr.Recognizer()
while True:
    with sr.Microphone() as source:
        print("Hola, soy tu asistente por voz: ")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="es-ES")
            print("Has dicho: {}".format(text))
            print(text)
            
            # Responde a la voz
            if text.lower() == "hola":
                print("¿Qué tal?")
            
            # Abrir Brave
            elif text.lower() == "internet":
                print("Abriendo el navegador Brave...")
                subprocess.Popen(["C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"])

            elif text.lower() == "youtube":
                webbrowser.open('https://youtube.com')

            elif text.lower() == "angelito":
                webbrowser.open('https://youtu.be/6UVzVdNZFKk?si=orpKb-nGbsCrjO__')

            # Salir si el usuario dice 'salir'
            elif text.lower() == "salir":
                print("Terminando el programa.")
                break
        except:
            print("No te he entendido")