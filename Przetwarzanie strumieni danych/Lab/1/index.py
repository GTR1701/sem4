import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class TaskLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Wybierz zadanie do uruchomienia")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centruj okno na ekranie
        self.center_window()
        
        # Główny frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tytuł
        title_label = ttk.Label(main_frame, text="Przetwarzanie strumieni danych", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Laboratorium 1", 
                                  font=("Arial", 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Lista dostępnych zadań
        self.tasks = [
            ("Zadanie 1", "zad1.py", "Generator sygnałów (chirp, superpozycja) z interfejsem"),
            ("Zadanie 4", "zad4.py", "Analiza sygnałów losowych (rand, randn)"),
            ("Zadanie 5", "zad5.py", "Przebiegi czasowe z rozkładu normalnego"),
            ("Zadanie 6", "zad6.py", "Generowanie szumu Browna"),
            ("Zadanie 7", "zad7.py", "Obrazy 2D z szumu Browna (podwójne cumsum)")
        ]
        
        # Tworzenie przycisków dla każdego zadania
        for i, (task_name, filename, description) in enumerate(self.tasks):
            # Frame dla każdego zadania
            task_frame = ttk.Frame(main_frame)
            task_frame.grid(row=i+2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            
            # Przycisk
            btn = ttk.Button(task_frame, text=task_name, width=15,
                           command=lambda f=filename: self.run_task(f))
            btn.grid(row=0, column=0, padx=(0, 10))
            
            # Opis
            desc_label = ttk.Label(task_frame, text=description, 
                                 font=("Arial", 9), foreground="gray")
            desc_label.grid(row=0, column=1, sticky=tk.W)
        
        # Przycisk wyjścia
        exit_btn = ttk.Button(main_frame, text="Wyjście", 
                             command=self.root.quit)
        exit_btn.grid(row=len(self.tasks)+3, column=0, columnspan=2, pady=20)
        
        # Konfiguracja grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def center_window(self):
        """Centruje okno na ekranie"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def run_task(self, filename):
        """Uruchamia wybrane zadanie"""
        try:
            # Pobierz pełną ścieżkę do pliku
            current_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(current_dir, filename)
            
            # Sprawdź czy plik istnieje
            if not os.path.exists(full_path):
                messagebox.showerror("Błąd", f"Plik {filename} nie został znaleziony!")
                return
            
            # Wyświetl potwierdzenie
            if messagebox.askyesno("Potwierdzenie", 
                                  f"Czy chcesz uruchomić {filename}?"):
                
                # Minimalizuj okno główne
                self.root.iconify()
                
                # Uruchom zadanie w nowym procesie - użyj pełnej ścieżki
                process = subprocess.Popen([sys.executable, full_path], 
                                         cwd=current_dir,
                                         creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
                
                # Opcjonalnie: przywróć okno po zakończeniu zadania
                self.root.after(1000, lambda: self.check_process(process))
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się uruchomić zadania:\n{str(e)}")
    
    def check_process(self, process):
        """sprawdza czy proces jest nadal aktywny"""
        if process.poll() is None:
            # Proces nadal działa, sprawdź ponownie za sekundę
            self.root.after(1000, lambda: self.check_process(process))
        else:
            # Proces się zakończył, przywróć okno
            self.root.deiconify()

def main():
    """Główna funkcja uruchamiająca aplikację"""
    root = tk.Tk()
    app = TaskLauncher(root)
    
    # Obsługa zamknięcia okna
    def on_closing():
        if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć aplikację?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Uruchom aplikację
    root.mainloop()

if __name__ == "__main__":
    main()
