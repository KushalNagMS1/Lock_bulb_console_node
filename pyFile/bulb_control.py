import speech_recognition as sr
from gtts import gTTS
import os
# import pygame
import uuid
import sys
import os
import json
import google.generativeai as genai

# Set up Google Gemini API
GOOGLE_API_KEY = 'AIzaSyDkJ9DZKzni25puzf83PDZQEDRUb81M4V8'
genai.configure(api_key=GOOGLE_API_KEY)


# generation_config = {
#     "temperature": 0.7,
#     "top_p": 1,
#     "top_k": 1,
#     "max_output_tokens": 2048,
# }

# safety_settings = [
#     {
#         "category": "HARM_CATEGORY_HARASSMENT",
#         "threshold": "BLOCK_NONE"
#     },
#     {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "threshold": "BLOCK_NONE"
#     },
#     {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "threshold": "BLOCK_NONE"
#     },
#     {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "threshold": "BLOCK_NONE"
#     },
# ]

# model = genai.GenerativeModel('gemini-1.5-flash',
#                               generation_config=generation_config,
#                               safety_settings=safety_settings)
# convo = model.start_chat()

# def text_to_speech(text, language='en'):
#     filename = f"output_{uuid.uuid4()}.mp3"
#     tts = gTTS(text=text, lang=language)
#     tts.save(filename)
#     os.chmod(filename, 0o666)
#     pygame.mixer.init()
#     print("reached here")
#     pygame.mixer.music.load(filename)
#     pygame.mixer.music.play()
#     print("Reached here")
#     while pygame.mixer.music.get_busy():
#         pygame.time.Clock().tick(10)
#     pygame.mixer.quit()
#     os.remove(filename)  # <--- Add this line to delete the file after playback

def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone(device_index=0) as source:
        r.adjust_for_ambient_noise(source)
        
        try:
            audio = r.listen(source, timeout=10)
            text = r.recognize_google(audio).lower()
            
            # if text == "goodbye":
            #     sys.exit(0)
            
            # convo.send_message(text)
            # response = convo.last.text
            # response = response.replace('#', '').replace('*', '')
            return text
            # text_to_speech(response)
        
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            pass  


# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
  system_instruction="You are a chatbot that also controls smart home devices. The user can have a general conversation with your or use you to control the smart home devices.\n\nYour response should be in json format :\n\nresponse : \"Response to user's query\"/ \"device turned ON/OFF\",\ndevice_name : \"ledPin\" / NaN\ndevice_status : ON/ OFF\n\n\n----\n\nAll you need to do is detect if user is talking about a smart device or not.\nIf the user is talking about a smart device I need you to update the \"device_status \"and mention the device name under \"device_name\" and the response should be something like this \"Device turned ON\".\n your response should be something like this :\n{\nresponse : \"LED turned ON\"\ndevice_name : LED\ndevice_status : \"ON\"\n}\n----\nIf user is not talking about any smart device, example \"Who is the Prime Minister of India?\", your response should be something like this :\n{\nresponse : \"The PM of India is Narendra Modi\"\ndevice_name : NaN\ndevice_status : \"OFF\"\n}\n",
)

chat_session = model.start_chat(
  
)

def getJson(string):
    first= string.find('{')
    last= string.rfind('}')+1
    json_string= string[first:last]
    return json_string
user_query=speech_to_text()
if user_query:
    response = chat_session.send_message(user_query)
    output=getJson(response.text)

    print(output)

else:
    pass








