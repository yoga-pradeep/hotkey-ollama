# Bilingual Assistant for Hindi and Tamil Translations
# Final Corrected Version: August 10, 2025

import requests
import json
import tkinter as tk
from tkinter import messagebox
import pyperclip
import pyautogui
from pynput import keyboard
import time
import threading

# --- Configuration ---
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma:2b" # Or whichever Gemma model you have running

# --- Core Translation Function ---
def get_gemma_translation(text: str, task: str):
    prompt = ""
    if task == "to_english":
        prompt = (f"You are an expert linguist. The following text is either in Hindi or Tamil. "
                  f"Detect the language and translate it to modern, fluent English. "
                  f"Provide ONLY the English translation.\n\nText: \"{text}\"\n\nEnglish Translation:")
    elif task == "to_hindi":
        prompt = (f"You are an expert English-to-Hindi translator. Translate the following English text "
                  f"into Hindi using the Devanagari script. Provide ONLY the Hindi translation.\n\n"
                  f"English Text: \"{text}\"\n\nHindi Translation:")
    elif task == "to_tamil":
        prompt = (f"You are an expert English-to-Tamil translator. Translate the following English text "
                  f"into Tamil using the Tamil script. Provide ONLY the Tamil translation.\n\n"
                  f"English Text: \"{text}\"\n\nTamil Translation:")
    else:
        return "Error: Invalid task selected."

    try:
        payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        suggestion = response_data.get("response", "").strip()
        if suggestion.startswith('"') and suggestion.endswith('"'):
            suggestion = suggestion[1:-1]
        return suggestion
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to Ollama. Is it running?"
    except Exception as e:
        return f"An unknown error occurred: {e}"

# --- User Interface (GUI Popups) ---
def show_task_selection_popup():
    root = tk.Tk()
    root.title("Choose Action")
    root.geometry("350x150")
    root.attributes('-topmost', True)
    user_choice = tk.StringVar()
    def set_choice(choice):
        user_choice.set(choice)
        root.destroy()
    tk.Label(root, text="What would you like to do?", font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Translate to English", command=lambda: set_choice("to_english")).pack(fill="x", padx=20, pady=5)
    tk.Button(root, text="Translate to Hindi (हिन्दी)", command=lambda: set_choice("to_hindi")).pack(fill="x", padx=20, pady=5)
    tk.Button(root, text="Translate to Tamil (தமிழ்)", command=lambda: set_choice("to_tamil")).pack(fill="x", padx=20, pady=5)
    root.mainloop()
    return user_choice.get()

def show_review_popup(original_text: str, suggested_text: str):
    if not suggested_text or suggested_text.startswith("Error"):
        messagebox.showerror("Translation Error", suggested_text)
        return False
    root = tk.Tk()
    root.title("Translation Suggestion")
    root.geometry("600x400")
    root.attributes('-topmost', True)
    user_choice = tk.BooleanVar()
    tk.Label(root, text="Original Text:", font=("Arial", 10, "bold")).pack(pady=(10,0))
    original_frame = tk.Frame(root); original_frame.pack(pady=5, padx=10, fill="x", expand=True)
    original_text_widget = tk.Text(original_frame, height=6, wrap="word"); original_text_widget.insert("1.0", original_text)
    original_text_widget.config(state="disabled"); original_text_widget.pack(side="left", fill="both", expand=True)
    tk.Label(root, text="Suggested Translation:", font=("Arial", 10, "bold")).pack(pady=(10,0))
    suggested_frame = tk.Frame(root); suggested_frame.pack(pady=5, padx=10, fill="x", expand=True)
    suggested_text_widget = tk.Text(suggested_frame, height=6, wrap="word"); suggested_text_widget.insert("1.0", suggested_text)
    suggested_text_widget.pack(side="left", fill="both", expand=True)
    def accept_suggestion():
        final_text = suggested_text_widget.get("1.0", "end-1c")
        pyperclip.copy(final_text); user_choice.set(True); root.destroy()
    def decline_suggestion():
        user_choice.set(False); root.destroy()
    button_frame = tk.Frame(root); button_frame.pack(pady=20)
    tk.Button(button_frame, text="Accept & Replace", command=accept_suggestion).pack(side="left", padx=10)
    tk.Button(button_frame, text="Cancel", command=decline_suggestion).pack(side="left", padx=10)
    root.protocol("WM_DELETE_WINDOW", decline_suggestion); root.mainloop()
    return user_choice.get()

# --- Main Application Logic ---
def run_assistant():
    original_clipboard = pyperclip.paste()
    pyperclip.copy("")
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    selected_text = pyperclip.paste()
    if not selected_text:
        pyperclip.copy(original_clipboard)
        return
    chosen_task = show_task_selection_popup()
    if not chosen_task:
        pyperclip.copy(original_clipboard)
        return
    suggestion = get_gemma_translation(selected_text, chosen_task)
    if show_review_popup(selected_text, suggestion):
        pyautogui.hotkey('ctrl', 'v')
    else:
        pyperclip.copy(original_clipboard)

# --- Hotkey Listener (Revised and Corrected) ---
hotkey_running = False
def on_activate():
    """Wrapper function to prevent the hotkey from running multiple times at once."""
    global hotkey_running
    if not hotkey_running:
        hotkey_running = True
        # Run the main logic in a new thread to avoid freezing the listener
        assistant_thread = threading.Thread(target=run_assistant)
        assistant_thread.start()
        assistant_thread.join() # Wait for the thread to finish
        hotkey_running = False

def main():
    """Main function to set up and run the hotkey listener."""
    print("Bilingual assistant is running...")
    print("Select text and press <Ctrl>+- to translate.")
    
    # This is the stable way to define and listen for a global hotkey.
    # It maps a string representation of the hotkey to the function to be called.
    hotkeys = {
        '<ctrl>+-': on_activate
    }

    # The GlobalHotKeys listener runs in the background.
    with keyboard.GlobalHotKeys(hotkeys) as listener:
        listener.join()

if __name__ == "__main__":
    main()
