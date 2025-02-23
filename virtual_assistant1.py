import speech_recognition as aa
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import time
import threading

# Spotify credentials
SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
SPOTIPY_REDIRECT_URI = ''

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-modify-playback-state,user-read-playback-state"))

listener = aa.Recognizer()
machine = pyttsx3.init()

def talk(text):
    machine.say(text)
    machine.runAndWait()

def input_instruction():
    try:
        with aa.Microphone() as origin:
            print("Microphone is on")
            listener.adjust_for_ambient_noise(origin)  # Adjust for ambient noise
            print("Listening...")
            speech = listener.listen(origin)
            print("Processing...")
            instruction = listener.recognize_google(speech)
            instruction = instruction.lower()
            if 'jarvis' in instruction:
                instruction = instruction.replace('jarvis', '').strip()
                print("Instruction after removing 'jarvis':", instruction)
            print("Instruction:", instruction)
            return instruction
    except aa.UnknownValueError:
        talk("Sorry, I did not get that")
        print("Sorry, I did not get that")
    except aa.RequestError:
        talk("Sorry, my speech service is down")
        print("Sorry, my speech service is down")
    except Exception as e:
        talk("An error occurred: " + str(e))
        print("An error occurred: " + str(e))
    return ""

def get_weather(city):
    api_key = 'Replace with your openweathermapapi'
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(base_url)
    data = response.json()
    print(f"Weather API response: {data}")  # Debugging statement
    if data['cod'] == 200:
        main = data['main']
        weather = data['weather'][0]
        temperature = main['temp']
        description = weather['description']
        talk(f'The temperature in {city} is {temperature} degrees Celsius with {description}.')
        print(f'The temperature in {city} is {temperature} degrees Celsius with {description}.')
    else:
        talk('City not found.')
        print('City not found.')

def get_news():
    api_key = 'newsapikey'
    base_url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(base_url)
    data = response.json()
    if data['status'] == 'ok':
        articles = data['articles'][:5]
        for i, article in enumerate(articles, 1):
            talk(f'News {i}: {article["title"]}')
            print(f'News {i}: {article["title"]}')
    else:
        talk('Unable to fetch news.')
        print('Unable to fetch news.')

def set_reminder(reminder, minutes):
    def reminder_thread():
        time.sleep(minutes)
        talk(f'Reminder: {reminder}')
        print(f'Reminder: {reminder}')
    threading.Thread(target=reminder_thread).start()

def play_jarvis():
    instruction = input_instruction()
    if 'play' in instruction:
        song = instruction.replace('play', '').strip()
        talk('playing ' + song)
        print('playing ' + song)
        # Search for the song on Spotify
        results = sp.search(q=song, limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            # Get the user's devices
            devices = sp.devices()
            if devices['devices']:
                device_id = devices['devices'][0]['id']
                # Play the song on the first available device
                sp.start_playback(device_id=device_id, uris=[track_uri])
            else:
                talk("No active devices found")
                print("No active devices found")
        else:
            talk("Song not found on Spotify")
            print("Song not found on Spotify")
    elif 'time' in instruction:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk('Current time is ' + time)
        print('Current time is ' + time)
    elif 'date' in instruction:
        date = datetime.datetime.now().strftime('%d %B %Y')
        talk("Current date is " + date)
        print("Current date is " + date)
    elif 'how are you' in instruction:
        talk('I am fine, thank you for asking')
        print('I am fine, thank you for asking')
    elif 'what is your name' in instruction:
        talk('I am Jarvis, your personal assistant')
        print('I am Jarvis, your personal assistant')
    elif 'who is' in instruction:
        person = instruction.replace('who is', '').strip()
        info = wikipedia.summary(person, 1)
        talk(info)
        print(info)
    elif 'weather' in instruction:
        talk('For which city?')
        city = input_instruction()
        print(f"Recognized city: {city}")  # Debugging statement
        get_weather(city)
    elif 'news' in instruction:
        get_news()
    elif 'remind' in instruction:
        reminder = instruction.replace('remind me to', '').strip()
        talk('In how many minutes?')
        minutes = int(input_instruction())
        set_reminder(reminder, minutes * 60)
        talk(f'Reminder set for {reminder} in {minutes} minutes')
    else:
        talk('I am not able to understand, please say the command again')
        print('I am not able to understand, please say the command again')

if __name__ == "__main__":
    play_jarvis()