import tkinter as tk
from tkinter import messagebox
from pynput import mouse, keyboard
import threading
import time

class MacroRecorder:
    def __init__(self, master):
        self.master = master
        self.master.title("Macro Recorder")
        
        self.recording = False
        self.actions = []
        self.clicking = False
        self.click_thread = None
        self.click_position = None
        
        self.start_button = tk.Button(master, text="Começar a Gravar", command=self.start_recording)
        self.start_button.pack(pady=10)
        
        self.stop_button = tk.Button(master, text="Parar Gravação", command=self.stop_recording)
        self.stop_button.pack(pady=10)
        self.stop_button.config(state=tk.DISABLED)
        
        self.play_button = tk.Button(master, text="Reproduzir Macro", command=self.play_macro)
        self.play_button.pack(pady=10)
        self.play_button.config(state=tk.DISABLED)
        
        self.start_click_button = tk.Button(master, text="Iniciar Clique Contínuo", command=self.start_continuous_click)
        self.start_click_button.pack(pady=10)
        
        self.stop_click_button = tk.Button(master, text="Parar Clique Contínuo", command=self.stop_continuous_click)
        self.stop_click_button.pack(pady=10)
        self.stop_click_button.config(state=tk.DISABLED)
        
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        
        self.esc_listener = keyboard.Listener(on_press=self.on_esc_press)
        self.esc_listener.start()
    
    def start_recording(self):
        self.recording = True
        self.actions = []
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.DISABLED)
        
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.mouse_listener.start()
        self.keyboard_listener.start()
        messagebox.showinfo("Informação", "Gravação Iniciada!")
    
    def stop_recording(self):
        self.recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)
        
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        messagebox.showinfo("Informação", "Gravação Parada!")
    
    def on_click(self, x, y, button, pressed):
        if self.recording:
            action = ('mouse_click', x, y, button, pressed, time.time())
            self.actions.append(action)
    
    def on_press(self, key):
        if self.recording:
            action = ('key_press', key, time.time())
            self.actions.append(action)
    
    def play_macro(self):
        if not self.actions:
            messagebox.showwarning("Aviso", "Nenhuma ação gravada!")
            return
        
        start_time = self.actions[0][-1]
        for action in self.actions:
            if action[0] == 'mouse_click':
                _, x, y, button, pressed, action_time = action
                delay = action_time - start_time
                threading.Timer(delay, self.execute_mouse_click, args=[x, y, button, pressed]).start()
            elif action[0] == 'key_press':
                _, key, action_time = action
                delay = action_time - start_time
                threading.Timer(delay, self.execute_key_press, args=[key]).start()
    
    def execute_mouse_click(self, x, y, button, pressed):
        with mouse.Controller() as m_controller:
            m_controller.position = (x, y)
            if pressed:
                m_controller.press(button)
            else:
                m_controller.release(button)
    
    def execute_key_press(self, key):
        with keyboard.Controller() as k_controller:
            k_controller.press(key)
            k_controller.release(key)
    
    def start_continuous_click(self):
        self.click_position = None
        
        def get_click_position(x, y, button, pressed):
            if pressed:
                self.click_position = (x, y)
                self.mouse_listener.stop()
                self.mouse_listener = mouse.Listener(on_click=self.on_click)
                self.mouse_listener.start()
                self.start_continuous_click_thread()
        
        self.mouse_listener.stop()
        self.mouse_listener = mouse.Listener(on_click=get_click_position)
        self.mouse_listener.start()
        
        messagebox.showinfo("Informação", "Clique no local onde deseja iniciar o clique contínuo.")
    
    def start_continuous_click_thread(self):
        if self.click_position:
            self.clicking = True
            self.start_click_button.config(state=tk.DISABLED)
            self.stop_click_button.config(state=tk.NORMAL)
            self.click_thread = threading.Thread(target=self.continuous_click, args=self.click_position)
            self.click_thread.start()
    
    def continuous_click(self, x, y):
        with mouse.Controller() as m_controller:
            while self.clicking:
                m_controller.position = (x, y)
                m_controller.click(mouse.Button.left)
                time.sleep(0.1)  # Ajuste o intervalo de tempo entre os cliques conforme necessário
    
    def stop_continuous_click(self):
        self.clicking = False
        if self.click_thread:
            self.click_thread.join()
        self.start_click_button.config(state=tk.NORMAL)
        self.stop_click_button.config(state=tk.DISABLED)
        messagebox.showinfo("Informação", "Clique contínuo parado.")
    
    def on_esc_press(self, key):
        if key == keyboard.Key.esc:
            self.stop_all_actions()
    
    def stop_all_actions(self):
        self.recording = False
        self.clicking = False
        
        if self.mouse_listener.running:
            self.mouse_listener.stop()
        
        if self.keyboard_listener.running:
            self.keyboard_listener.stop()
        
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)
        self.start_click_button.config(state=tk.NORMAL)
        self.stop_click_button.config(state=tk.DISABLED)
        
        messagebox.showinfo("Informação", "Todas as ações foram paradas!")

# Executar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorder(root)
    root.mainloop()
