from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import scrolledtext
import threading
import webbrowser
import speech_recognition as sr
from gtts import gTTS
import os
import time
import requests

class MichelleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Michelle - Asisten Virtual")

        # API Keys
        self.weather_api_key = "cbae3107a10f1981ad8ba0474cf6d2dc"
        self.geoapify_api_key = "b14689f4b795451b96b71d1f49b26f53"

        # Warna latar belakang dan teks
        self.bg_color = "#f0f0f0"
        self.text_color = "#333333"
        self.button_color = "#f0f0f0"
        self.button_hover_color = "#f0f0f0"

        # Setting gaya
        self.root.configure(bg=self.bg_color)
        self.root.geometry("600x500")

        self.label = tk.Label(root, text="Michelle - Asisten Virtual", font=("Arial", 24), bg=self.bg_color, fg=self.text_color)
        self.label.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10, font=("Arial", 14), bg="white", fg=self.text_color)
        self.text_area.pack(padx=10, pady=10)
        self.text_area.insert(tk.END, "Silakan mulai dengan mengklik tombol 'Mulai Mendengarkan' dan ucapkan pertanyaan atau perintah Anda seperti:\n\n"
                                      "- 'Silahkan ucapkan hai'\n"
                                      "- 'siapa nama kamu atau what is your name'\n"
                                      "- 'apa kabar'\n"
                                      "- 'Bisa Tolong saya'\n\n"
                                      "- 'putar lagu di YouTube'\n"
                                      "- 'buka lagu yang bagus di YouTube'\n"
                                      "- 'tutup lagu di YouTube'\n")

        # Tombol 'Mulai Mendengarkan' dalam bentuk lingkaran dengan ikon mic
        self.listen_button_img = self.rounded_button_image("mic_icon.png", self.button_color, self.button_hover_color)
        self.listen_button = tk.Button(root, image=self.listen_button_img, command=self.run_michelle, bd=0, bg=self.bg_color)
        self.listen_button.image = self.listen_button_img
        self.listen_button.pack(pady=10)

        # Tombol 'Keluar'
        self.stop_button = tk.Button(root, text="Keluar", command=root.quit, font=("Arial", 14), bg="red", fg="white", bd=0)
        self.stop_button.pack(pady=10)
        self.stop_button.bind("<Enter>", lambda event, h=self.stop_button_hover(): h.configure(bg="#d32f2f"))
        self.stop_button.bind("<Leave>", lambda event, h=self.stop_button_hover(): h.configure(bg="red"))

    def stop_button_hover(self):
        return self.stop_button

    def rounded_button_image(self, icon_path, bg_color, hover_color):
        size = 70  # Ukuran gambar tombol
        img = Image.new("RGBA", (size, size), bg_color)
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size, size), fill=bg_color, outline=bg_color)

        # Memuat ikon mic dan menempatkannya di tengah gambar
        icon = Image.open(icon_path).convert("RGBA")
        icon = icon.resize((int(size * 0.6), int(size * 0.6)), Image.LANCZOS)
        img.paste(icon, (int((size - icon.width) / 2), int((size - icon.height) / 2)), icon)

        # Membuat versi hover dengan blending alpha
        hover_img = Image.new("RGBA", (size, size), hover_color + "80")
        img_hover = Image.alpha_composite(img, hover_img)

        return ImageTk.PhotoImage(img_hover)

    def perintah(self):
        mendengar = sr.Recognizer()
        with sr.Microphone() as source:
            self.text_area.insert(tk.END, "Mendengarkan....\n")
            self.text_area.see(tk.END)
            suara = mendengar.listen(source, phrase_time_limit=5)
            try:
                self.text_area.insert(tk.END, "Diterima...\n")
                self.text_area.see(tk.END)
                dengar = mendengar.recognize_google(suara, language='id-ID')
                self.text_area.insert(tk.END, f"Anda: {dengar}\n")
                self.text_area.see(tk.END)
            except Exception as e:
                print(f"Error: {str(e)}")
                dengar = "Maaf saya tidak mendengar dengan jelas."
                self.text_area.insert(tk.END, f"{dengar}\n")
                self.text_area.see(tk.END)
            return dengar

    def ngomong(self, teks, bahasa='id'):
        namafile = 'Ngomong.mp3'
        suara = gTTS(text=teks, lang=bahasa, slow=False)
        suara.save(namafile)
        os.system(f'start {namafile}')
        self.text_area.insert(tk.END, f"Michelle: {teks}\n")
        self.text_area.see(tk.END)

    def generate_response(self, input_text, bahasa='id'):
        responses_id = {
            "hai": "Halo! Ada yang bisa saya bantu?",
            "siapa nama kamu": "Nama saya Michelle, asisten virtual Anda.",
            "apa kabar": "Saya baik-baik saja, terima kasih. Bagaimana dengan Anda?",
            "terima kasih": "Sama-sama! Ada yang lain yang bisa saya bantu?",
            "apakah kamu lapar": "Saya tidak lapar, bagaimana denganmu?",
            "saya lapar": "Apakah kamu ingin makan sekarang?",
            "makanan apa yang enak": "Bagaimana jika mencoba makan Mi Ayam?",
            "selesai": "Selamat tinggal! Semoga harimu menyenangkan.",
            "gombalin aku dong": "apa bedanya kamu sama matahari",
            "apa bedanya": "Matahari menyinari bumi kalau kamu menyinari hari-hariku.",
            "ada apa": "Silakan tanyakan pertanyaan atau perintah Anda.",
            "bisa tolong saya": "Tentu, saya siap membantu Anda.",
            "buka google": "Akan membuka Google untuk Anda.",
            "buka youtube": "Akan membuka YouTube untuk Anda.",
            "buka e-learning": "saya akan membukakan elearning untuk anda.",
            "putar lagu di youtube": "Sedang memutar lagu di YouTube.",
            "buka lagu yang bagus di youtube": "Sedang mencari lagu bagus di YouTube.",
            "tutup lagu": "Menutup pemutaran lagu di YouTube.",
            "cuaca hari ini": self.handle_weather_request()
        }

        responses_en = {
            "hi": "Hello! How can I assist you?",
            "what is your name": "My name is Michelle, your virtual assistant.",
            "how are you": "I'm fine, thank you. How about you?",
            "thank you": "You're welcome! Anything else I can help with?",
            "are you hungry": "I'm not hungry, how about you?",
            "i am hungry": "Would you like to eat now?",
            "what food is good": "How about trying Chicken Noodles?",
            "goodbye": "Goodbye! Have a great day.",
            "what's up": "Feel free to ask your question or command.",
            "open google": "I will open Google for you.",
            "open youtube": "I will open YouTube for you.",
            "open elearning": "I will open elearning for you.",
            "play a song on youtube": "Playing a song on YouTube.",
            "find a good song on youtube": "Searching for a good song on YouTube.",
            "close the song": "Closing the song on YouTube.",
            "what is the weather today": self.handle_weather_request()
        }

        if bahasa == 'id':
            for key, response in responses_id.items():
                if key in input_text.lower():
                    if key == "buka google":
                        self.buka_google()
                    elif key == "buka youtube":
                        self.buka_youtube()
                    elif key == "buka e-learning":
                        self.saya_mau_absen()
                    elif key == "putar lagu di youtube":
                        self.putar_lagu_di_youtube()
                    elif key == "tutup lagu":
                        self.tutup_lagu_di_youtube()
                    elif key == "cuaca hari ini":
                        return response
                    return response
        else:
            for key, response in responses_en.items():
                if key in input_text.lower():
                    if key == "open google":
                        self.buka_google()
                    elif key == "open youtube":
                        self.buka_youtube()
                    elif key == "open elearning":
                        self.saya_mau_absen()
                    elif key == "play a song on youtube":
                        self.play_song_on_youtube()
                    elif key == "close the song":
                        self.close_song_on_youtube()
                    elif key == "what is the weather today":
                        return response
                    return response

        return "Maaf, saya tidak mengerti. Bisa diulangi?" if bahasa == 'id' else "Sorry, I don't understand. Can you repeat?"

    def handle_weather_request(self):
        location = self.get_location()
        if location:
            weather = self.get_weather(location)
            if weather:
                return weather
        return "Maaf, saya tidak dapat mengambil data cuaca saat ini."

    def get_location(self):
        try:
            response = requests.get(f"https://api.geoapify.com/v1/ipinfo?apiKey={self.geoapify_api_key}")
            if response.status_code == 200:
                data = response.json()
                city = data.get("city", {}).get("name", "tidak diketahui")
                country = data.get("country", {}).get("name", "tidak diketahui")
                return f"{city}, {country}"
            else:
                print(f"Error fetching location: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting location: {str(e)}")
            return None

    def get_weather(self, location):
        try:
            response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}&units=metric")
            data = response.json()
            if data["cod"] == 200:
                main = data["weather"][0]["main"]
                description = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                return f"Cuaca di {location}: {main} ({description}), suhu {temp}°C."
            else:
                return "Tidak dapat mengambil data cuaca untuk lokasi tersebut."
        except Exception as e:
            print(f"Error getting weather: {str(e)}")
            return None

    def buka_google(self):
        webbrowser.open_new_tab("https://www.google.com")

    def buka_youtube(self):
        webbrowser.open_new_tab("https://www.youtube.com")

    def saya_mau_absen(self):
        webbrowser.open_new_tab("https://elearning.universitasputrabangsa.ac.id/my/")

    def putar_lagu_di_youtube(self):
        self.ngomong("Sedang memutar lagu di YouTube.")
        webbrowser.open_new_tab("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def play_song_on_youtube(self):
        self.ngomong("Playing a song on YouTube.")
        webbrowser.open_new_tab("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def tutup_lagu_di_youtube(self):
        self.ngomong("Menutup pemutaran lagu di YouTube.")
        self.close_song_on_youtube()

    def close_song_on_youtube(self):
        # Fungsi untuk menutup tab YouTube di sini
        pass

    def run_michelle(self):
        threading.Thread(target=self.process_michelle).start()

    def process_michelle(self):
        while True:
            Layanan = self.perintah()
            if any(word in Layanan.lower() for word in ['hi', 'hello', 'what', 'how', 'thank', 'are', 'yes', 'goodbye']):
                bahasa = 'en'
            else:
                bahasa = 'id'

            response = self.generate_response(Layanan, bahasa)
            self.ngomong(response, bahasa)
            time.sleep(5)
            if Layanan.lower() in ['keluar', 'selesai', 'exit', 'stop', 'goodbye']:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = MichelleApp(root)
    root.mainloop()
