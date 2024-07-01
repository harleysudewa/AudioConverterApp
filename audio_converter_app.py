import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from pydub import AudioSegment
import os
import threading
import simpleaudio as sa

class AudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Audio Converter")
        self.root.geometry("700x500")
        
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(pady=10, padx=10)

        self.label = tk.Label(self.main_frame, text="Advanced Audio Converter", font=("Arial", 16))
        self.label.grid(row=0, columnspan=2, pady=10)
        
        self.select_button = tk.Button(self.main_frame, text="Select File(s)", command=self.select_file)
        self.select_button.grid(row=1, column=0, pady=5, sticky="e")
        
        self.file_label = tk.Label(self.main_frame, text="No file selected", font=("Arial", 12))
        self.file_label.grid(row=1, column=1, pady=5, sticky="w")
        
        tk.Label(self.main_frame, text="Output Format", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky="e")
        self.format_combobox = Combobox(self.main_frame, values=["MP3", "WAV", "OGG", "FLAC"], state="readonly")
        self.format_combobox.grid(row=2, column=1, pady=5, sticky="w")
        self.format_combobox.current(0)
        
        tk.Label(self.main_frame, text="Bitrate (kbps)", font=("Arial", 12)).grid(row=3, column=0, pady=5, sticky="e")
        self.bitrate_combobox = Combobox(self.main_frame, values=["64", "128", "192", "256", "320"], state="readonly")
        self.bitrate_combobox.grid(row=3, column=1, pady=5, sticky="w")
        self.bitrate_combobox.current(1)
        
        tk.Label(self.main_frame, text="Start Time (seconds)", font=("Arial", 12)).grid(row=4, column=0, pady=5, sticky="e")
        self.start_time_entry = tk.Entry(self.main_frame)
        self.start_time_entry.grid(row=4, column=1, pady=5, sticky="w")
        
        tk.Label(self.main_frame, text="End Time (seconds)", font=("Arial", 12)).grid(row=5, column=0, pady=5, sticky="e")
        self.end_time_entry = tk.Entry(self.main_frame)
        self.end_time_entry.grid(row=5, column=1, pady=5, sticky="w")
        
        tk.Label(self.main_frame, text="Volume Change (dB)", font=("Arial", 12)).grid(row=6, column=0, pady=5, sticky="e")
        self.volume_entry = tk.Entry(self.main_frame)
        self.volume_entry.grid(row=6, column=1, pady=5, sticky="w")
        
        self.preview_button = tk.Button(self.main_frame, text="Preview", command=self.preview_audio)
        self.preview_button.grid(row=7, column=0, pady=5, sticky="e")
        
        self.convert_button = tk.Button(self.main_frame, text="Convert", command=self.convert_file)
        self.convert_button.grid(row=7, column=1, pady=5, sticky="w")
        
        self.file_paths = []
        self.converted_audio = None
    
    def select_file(self):
        self.file_paths = filedialog.askopenfilenames(
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")]
        )
        if self.file_paths:
            self.file_label.config(text=f"Selected: {', '.join(self.file_paths)}")
    
    def preview_audio(self):
        if not self.file_paths:
            messagebox.showwarning("No File Selected", "Please select file(s) first.")
            return
        
        self.converted_audio = self.process_audio(preview=True)
        if self.converted_audio:
            preview_path = "preview.wav"
            self.converted_audio.export(preview_path, format="wav")
            threading.Thread(target=self.play_audio, args=(preview_path,)).start()
    
    def play_audio(self, file_path):
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    
    def process_audio(self, preview=False):
        output_format = self.format_combobox.get().lower()
        bitrate = self.bitrate_combobox.get() + "k" if not preview else None
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()
        volume_change = self.volume_entry.get()
        
        try:
            combined_audio = AudioSegment.empty()
            
            for file_path in self.file_paths:
                audio = AudioSegment.from_file(file_path)
                
                if start_time:
                    start_time = int(start_time) * 1000
                else:
                    start_time = 0
                
                if end_time:
                    end_time = int(end_time) * 1000
                else:
                    end_time = len(audio)
                
                audio = audio[start_time:end_time]
                
                if volume_change:
                    volume_change = int(volume_change)
                    audio = audio + volume_change
                
                combined_audio += audio
            
            return combined_audio
        except Exception as e:
            messagebox.showerror("Processing Failed", f"An error occurred: {e}")
            return None
    
    def convert_file(self):
        if not self.file_paths:
            messagebox.showwarning("No File Selected", "Please select file(s) first.")
            return
        
        combined_audio = self.process_audio()
        if combined_audio:
            try:
                for file_path in self.file_paths:
                    output_format = self.format_combobox.get().lower()
                    bitrate = self.bitrate_combobox.get() + "k"
                    output_file = os.path.splitext(file_path)[0] + f"_converted.{output_format}"
                    combined_audio.export(output_file, format=output_format, bitrate=bitrate)
                
                messagebox.showinfo("Conversion Success", f"Files converted successfully.")
            except Exception as e:
                messagebox.showerror("Conversion Failed", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioConverterApp(root)
    root.mainloop()