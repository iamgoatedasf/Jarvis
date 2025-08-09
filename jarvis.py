from playsound import playsound
import os
import sys
import queue
import threading
import time
import random
import webbrowser
import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
import pyttsx3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QRadialGradient, QPen
from PyQt5.QtCore import Qt, QTimer, QPointF
from datetime import datetime
import requests

class MovingLine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        self.x1 = random.uniform(0, self.width)
        self.y1 = random.uniform(0, self.height)
        self.x2 = self.x1 + random.uniform(-50, 50)
        self.y2 = self.y1 + random.uniform(-50, 50)
        self.speed_x = random.uniform(-0.3, 0.3)
        self.speed_y = random.uniform(-0.3, 0.3)
        self.alpha = random.randint(50, 120)

    def move(self):
        self.x1 += self.speed_x
        self.y1 += self.speed_y
        self.x2 += self.speed_x
        self.y2 += self.speed_y

        # Bounce off edges
        if not (0 <= self.x1 <= self.width) or not (0 <= self.x2 <= self.width):
            self.speed_x = -self.speed_x
        if not (0 <= self.y1 <= self.height) or not (0 <= self.y2 <= self.height):
            self.speed_y = -self.speed_y

class Jarvis(QWidget):

    def initUI(self):
        self.setWindowTitle("J A R V I S")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.Window)

        self.show()

    def __init__(self):
        super().__init__()
        self.initUI()

        self.glow = 70.0
        self.glow_direction = 1
        self.speaking = False
        self.pulses = []

        self.active_mode = False
        self.active_mode_timeout = 30  # seconds of inactivity
        self.last_active_time = 0

        self.tts_lock = threading.Lock()
        self.audio_lock = threading.Lock()  # Initialize audio_lock here
        self.voice_rate = 190
        self.voice_volume = 1.0

        self.width = self.width()
        self.height = self.height()

        # Prepare moving lines background
        self.lines = [MovingLine(self.width, self.height) for _ in range(50)]

        # Get default mic index explicitly
        self.default_mic_index = self.get_default_mic_index()
        print(f"Using microphone device index: {self.default_mic_index}")

        # Init Porcupine wake word engine
        try:
            self.porcupine = pvporcupine.create(
                access_key="Porcupine_key",
                keywords=["jarvis"]
            )
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
                input_device_index=self.default_mic_index
            )
        except Exception as e:
            print(f"Porcupine/audio init failed: {e}")
            self.porcupine = None
            self.audio_stream = None

        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone(device_index=self.default_mic_index)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

        if self.porcupine and self.audio_stream:
            threading.Thread(target=self.listen_wake_word, daemon=True).start()

    def get_default_mic_index(self):
        p = pyaudio.PyAudio()
        default_index = None
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev.get('maxInputChannels') > 0:
                if 'default' in dev.get('name').lower():
                    p.terminate()
                    return i
        # fallback first available mic
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev.get('maxInputChannels') > 0:
                default_index = i
                break
        p.terminate()
        return default_index

    def speak_blocking(self, text):
        with self.tts_lock, self.audio_lock:
            try:
                time.sleep(0.1)  # small pre-delay
                engine = pyttsx3.init()
                engine.setProperty('rate', self.voice_rate)
                engine.setProperty('volume', self.voice_volume)
                voices = engine.getProperty('voices')
                # pick male-ish voice if available
                for v in voices:
                    if 'male' in v.name.lower():
                        engine.setProperty('voice', v.id)
                        break
                engine.say(text)
                engine.runAndWait()
                time.sleep(0.1)  # small post-delay
            except Exception as e:
                print(f"TTS error: {e}")

    def play_mp3_async(self, mp3_file):
        def play():
            with self.audio_lock:
                try:
                    playsound(mp3_file)
                except Exception as e:
                    print(f"Error playing MP3: {e}")
        threading.Thread(target=play, daemon=True).start()

    def dynamic_greeting(self):
        now = datetime.now().hour
        if 5 <= now < 12:
            return "Good morning, sir."
        elif 12 <= now < 18:
            return "Good afternoon, sir."
        else:
            return "Good evening, sir."

    def update_animation(self):
        self.glow += self.glow_direction * (1.2 if self.speaking else 0.6)
        if self.glow > 90.0 or self.glow < 50.0:
            self.glow_direction *= -1

        for line in self.lines:
            line.move()

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        center = rect.center()

        # Blue glowing orb Jarvis in center
        orb_radius = int(self.glow)
        gradient = QRadialGradient(center, orb_radius + 40)
        gradient.setColorAt(0.0, QColor(0, 180, 255, 255))
        gradient.setColorAt(0.5, QColor(0, 130, 255, 180))
        gradient.setColorAt(1.0, QColor(0, 80, 120, 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, orb_radius + 40, orb_radius + 40)

        # Inner orb core
        core_grad = QRadialGradient(center, orb_radius)
        core_grad.setColorAt(0.0, QColor(0, 220, 255, 255))
        core_grad.setColorAt(0.6, QColor(0, 150, 255, 220))
        core_grad.setColorAt(1.0, QColor(0, 80, 120, 50))
        painter.setBrush(core_grad)
        painter.drawEllipse(center, orb_radius, orb_radius)

        # Pulses on speak
        for pulse in self.pulses:
            alpha = max(0, int(pulse["alpha"]))
            pen = QPen(QColor(0, 200, 255, alpha), 2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center, int(pulse["radius"]), int(pulse["radius"]))

        # Update pulses for next frame
        for pulse in self.pulses:
            pulse["radius"] += 3.5
            pulse["alpha"] -= 4
        self.pulses = [p for p in self.pulses if p["alpha"] > 8]

    def say(self, text, mp3_file=None):
        self.speaking = True
        self.pulses.append({"radius": self.glow + 40.0, "alpha": 255})

        if mp3_file and os.path.exists(mp3_file):
            self.play_mp3_async(mp3_file)
        else:
            self.speak_blocking(text)

        time.sleep(0.2)
        self.speaking = False

    def listen_wake_word(self):
        print("Listening for wake word 'jarvis'...")
        if not self.porcupine or not self.audio_stream:
            print("Porcupine or audio stream not initialized. Wake-word disabled.")
            return

        while True:
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                if self.porcupine.process(pcm_unpacked) >= 0:
                    if not self.active_mode:
                        print("Wake word detected!")
                        self.active_mode = True
                        self.last_active_time = time.time()
                        self.say(self.dynamic_greeting())
                    else:
                        print("Wake word detected but already active.")
            except IOError as e:
                print(f"Audio input error: {e}")
                time.sleep(0.1)
            except Exception as e:
                print(f"Unexpected error in wake-word loop: {e}")
                time.sleep(0.1)

    def listen_command_loop(self):
        while True:
            if self.active_mode and (time.time() - self.last_active_time > self.active_mode_timeout):
                self.say("Going to sleep, sir.")
                self.active_mode = False
                break

            if not self.active_mode:
                time.sleep(0.3)
                continue

            print("Listening for command...")
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                try:
                    audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=8)
                    command = self.recognizer.recognize_google(audio).lower()
                    print(f"Heard: {command}")
                    self.last_active_time = time.time()

                    if "go to sleep" in command or "stop listening" in command or "sleep" in command:
                        self.say("Understood.")
                        self.active_mode = False
                        break

                    self.handle_command(command)
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    print("what was that?")
                except sr.WaitTimeoutError:
                    print("Timeout")
                    print("what was that?")
                except Exception as e:
                    print(f"Error: {e}")
                    print("what was that?")
            time.sleep(0.3)

    def handle_command(self, command):
        command = command.lower().strip()
        print(f"[DEBUG] processed command: {command}")

        if "whats weather" or "weather" in command:
            self.say("Calculating...")
            weather_text = self.weather()
            self.say(weather_text)
            print (weather_text)
            return

        if "what are you" in command:
            self.say("", mp3_file = "R_U.mp3")
            return

        if "who should i trust" in command:
            self.say("", mp3_file = "friends.mp3")
            return

        if "the mission" in command or "whats the mission" in command:
            self.say("", mp3_file = "mission.mp3")
            return

        if "are humans worthy" in command or "are humans worth" in command:
            self.say ("", mp3_file = "speech.mp3")
            return

        if command.startswith ("open "):
            site = command.replace("open ", "").strip()
            site_clean = site.replace("http://", "").replace("https://", "").replace("www.", "").split()[0]
            if '.' not in site_clean:
                site_clean += ".com"
            url = f"https://{site_clean}"
            print(f"Opening URL: {url}")
            self.say("Right away, sir.")
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"Failed to open URL: {e}")
                self.say("I couldn't open that site, sir.")
            return

        self.say("Sorry, I can only open sites and answer a few questions right now.")

    def weather(self):
        api_key = "Weather_API_key"
        city = "Current_Location"
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            if data.get("weather") and data.get("main"):
                desc = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                return f"It is currently {temp} degrees Celsius with {desc}, sir."
            else:
                return "Sorry, I couldn't fetch the weather right now, sir."
        except Exception as e:
            print(f"Weather API error: {e}")
            return "Sorry, I couldn't fetch the weather right now, sir."

    def run(self):
        while True:
            if self.active_mode:
                self.listen_command_loop()
            else:
                time.sleep(0.3)

def main():
    app = QApplication(sys.argv)
    jarvis = Jarvis()
    threading.Thread(target=jarvis.run, daemon=True).start()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
