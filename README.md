# Jarvis
This is a Python-based voice assistant named **J.A.R.V.I.S.** built using **PyQt5** for the graphical interface, **Porcupine** for wake word detection, and **SpeechRecognition** for converting speech to text.

## Features:
- **Wake Word Detection:** Uses **Porcupine** to listen for the wake word ("Jarvis").
- **Speech-to-Text:** Converts spoken commands to text using **SpeechRecognition**.
- **Text-to-Speech:** Responds using a **pyttsx3** powered voice.
- **Weather Info:** Fetches real-time weather data using **OpenWeather API**.
- **Open Websites:** Opens websites via voice commands.
- **Customizable:** Modify the wake word and commands to suit your needs.
- **Background Animation:** Displays a dynamic moving line animation to enhance the UI.

**"What's the weather?"**  
   Fetches the current weather for Addis Ababa.

2. **"Open [website]"**  
   Opens a website via voice command. Example:  
   - "Open Google" → Opens `https://www.google.com`
   - "Open YouTube" → Opens `https://www.youtube.com`

3. **"Go to sleep" / "Stop listening" / "Sleep"**  
   Deactivates listening mode and puts J.A.R.V.I.S. to sleep.

4. **"What are you?"**  
   J.A.R.V.I.S. will respond with an audio file

5. **"Who should I trust?"**  
   J.A.R.V.I.S. will respond with an audio file

6. **"The mission" / "What's the mission?"**  
   J.A.R.V.I.S. will play an audio file related to the mission 

7. **"Are humans worthy?" / "Are humans worth?"**  
   J.A.R.V.I.S. will respond with an audio file 

8. **"Jarvis"**  
   Wake word to activate the assistant (listens for this word to start the command cycle).

9. **"Go to sleep"**  
   Stops listening for further commands and puts the assistant to sleep.
  
# The vision is peace in our time
The libraries required to be installed are:
# pyttsx3, SpeechRecognition, Pyaudio, Playsound, PyQt5, pvporcupine, Requests
- you can install these libraries using the pip command
  pip install {needed libraries}
  
  # For the wake word of porcupine
  - you need to sign in to Picovoice Consule and get an API key
    
  # For OpenWeatherAPI
   You’ll need to sign up for an API key on OpenWeatherMap and replace the placeholder api_key in the code.
  
## Additional Points:
- PyQt5==5.15.6
- playsound==1.2.2
- pyaudio==0.2.11
- SpeechRecognition==3.8.1
- pyttsx3==2.90
- pvporcupine==1.11.0
- requests==2.28.1
  
## Note
- make sure all the files are in the same folder, and I reccomend using a virtual environment.

### This ensures that when others clone my repo, they can install all the necessary libraries.

# Future advancements are coming



