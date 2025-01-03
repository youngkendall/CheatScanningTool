import os
import string
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import win32file
import win32api
from threading import Thread

WEBHOOK_URL = 'https://discord.com/api/webhooks/1324500041926312139/MrrRUVdZnfVwD7aOm228L9aTmpXp8mY9BXlxHVyK2oZtUg6p_leprbWhKJGJOnCaGZtb'

known_cheats = ['d3d10.dll', 'chrome.exe', 'public.zip', 'loader.exe', 'public.rar', 'password_is_eulen.rar',
                'password_is_eulen.zip', 'ovisetup.exe', 'USBDeview.exe', 'runtimebroker.exe',
                'cheats.rar', 'cheats.zip', 'rp.rar', 'RP.rar', 'Roleplay.rar', 'Roleplay.zip']
found_cheats = []
deleted_files = []
usb_devices = [] 
scan_running = False

--Test

def send_webhook_message(embed):
    """Send a message to the Discord webhook."""
    data = {"embeds": [embed]}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("Webhook-Nachricht erfolgreich gesendet.")
        else:
            print(f"Fehler beim Senden der Nachricht. Statuscode: {response.status_code}")
            print(f"Antwort von Discord: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Verbinden mit Webhook: {e}")

def format_cheat_paths(paths):
    """Format the paths for display in the Discord webhook."""
    return "\n".join(paths)

def scan_drive(drive):
    """Scan a single drive for known cheats."""
    for root, dirs, files in os.walk(drive):
        for file in files:
            if file.lower() in [cheat.lower() for cheat in known_cheats]:
                file_path = os.path.join(root, file)
                print(f"Gefundene Datei: {file_path}")
                found_cheats.append(file_path)

def scan_usb_devices():
    """Scan all connected USB devices."""
    global usb_devices
    usb_devices.clear()
    drives = [drive for drive in win32api.GetLogicalDriveStrings().split('\000') if drive]
    for drive in drives:
        if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
            print(f"USB-Gerät gefunden: {drive}")
            usb_devices.append(drive)
            scan_drive(drive)

def scan_all_drives():
    """Scan all drives including USB devices and hard disks."""
    print("Scanne alle verfügbaren Laufwerke...")
    drives = [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]
    for drive in drives:
        print(f"Scanne Laufwerk: {drive}")
        scan_drive(drive)

def scan_recycle_bin():
    """Scan the recycle bin for deleted files."""
    recycle_bin_path = r"C:\\$Recycle.Bin"
    if os.path.exists(recycle_bin_path):
        for drive in string.ascii_uppercase:
            drive_path = f"{drive}:\\$Recycle.Bin"
            if os.path.exists(drive_path):
                for root, dirs, files in os.walk(drive_path):
                    for file in files:
                        deleted_file_path = os.path.join(root, file)
                        deleted_files.append(deleted_file_path)

def start_scan():
    """Start the scan in a separate thread."""
    global scan_running
    if scan_running:
        messagebox.showwarning("Warnung", "Ein Scan läuft bereits.")
        return

    scan_running = True
    Thread(target=monitor_changes).start()

def stop_scan():
    """Stop the running scan."""
    global scan_running
    if scan_running:
        scan_running = False
        messagebox.showinfo("Scan gestoppt", "Der Scan wurde erfolgreich gestoppt.")
    else:
        messagebox.showwarning("Warnung", "Kein Scan läuft derzeit.")

def monitor_changes():
    """Monitor changes and perform the scan."""
    global scan_running
    found_cheats.clear()
    deleted_files.clear()
    usb_devices.clear()

    scan_all_drives()
    scan_usb_devices()
    scan_recycle_bin()

    if scan_running:
        update_ui()
        send_webhook_summaries()

def send_webhook_summaries():
    """Send summaries of the scans to the webhook."""
    if found_cheats:
        embed_cheats = {
            "title": "Gefundene Cheat-Dateien",
            "description": format_cheat_paths(found_cheats),
            "color": 0xFF0000,
            "footer": {"text": "Scan durchgeführt durch dein Tool"}
        }
        send_webhook_message(embed_cheats)

    if deleted_files:
        embed_deleted = {
            "title": "Dateien im Papierkorb",
            "description": format_cheat_paths(deleted_files),
            "color": 0xFFFF00,
            "footer": {"text": "Scan durchgeführt durch dein Tool"}
        }
        send_webhook_message(embed_deleted)

    if usb_devices:
        embed_usb = {
            "title": "Angeschlossene USB-Geräte",
            "description": format_cheat_paths(usb_devices),
            "color": 0x0000FF,
            "footer": {"text": "Scan durchgeführt durch dein Tool"}
        }
        send_webhook_message(embed_usb)
    else:
        send_webhook_message({
            "title": "USB-Scan abgeschlossen",
            "description": "Keine USB-Geräte gefunden.",
            "color": 0x00FF00,
            "footer": {"text": "Scan durchgeführt durch dein Tool"}
        })

def update_ui():
    """Update the UI lists with the scan results."""
    cheats_list.delete(0, tk.END)
    recycle_list.delete(0, tk.END)
    usb_list.delete(0, tk.END)

    for cheat in found_cheats:
        cheats_list.insert(tk.END, cheat)

    for deleted_file in deleted_files:
        recycle_list.insert(tk.END, deleted_file)

    for usb_device in usb_devices:
        usb_list.insert(tk.END, usb_device)

def create_gui():
    """Create the main GUI for the application."""
    global cheats_list, recycle_list, usb_list

    root = tk.Tk()
    root.title("Cheat-Scan-Tool")
    root.geometry("600x500")
    root.configure(bg="#282C34")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    cheats_frame = tk.Frame(notebook, bg="#282C34")
    notebook.add(cheats_frame, text="Gefundene Cheats")

    cheats_list = tk.Listbox(cheats_frame, bg="#1E2228", fg="white", font=("Arial", 10), height=10)
    cheats_list.pack(fill="both", expand=True, padx=5, pady=5)

    recycle_frame = tk.Frame(notebook, bg="#282C34")
    notebook.add(recycle_frame, text="Papierkorb-Dateien")

    recycle_list = tk.Listbox(recycle_frame, bg="#1E2228", fg="white", font=("Arial", 10), height=10)
    recycle_list.pack(fill="both", expand=True, padx=5, pady=5)

    usb_frame = tk.Frame(notebook, bg="#282C34")
    notebook.add(usb_frame, text="USB-Geräte")

    usb_list = tk.Listbox(usb_frame, bg="#1E2228", fg="white", font=("Arial", 10), height=10)
    usb_list.pack(fill="both", expand=True, padx=5, pady=5)

    button_frame = tk.Frame(root, bg="#282C34")
    button_frame.pack(pady=10)

    start_button = ttk.Button(button_frame, text="Scan starten", command=start_scan)
    start_button.grid(row=0, column=0, padx=10)

    stop_button = ttk.Button(button_frame, text="Scan stoppen", command=stop_scan)
    stop_button.grid(row=0, column=1, padx=10)

    quit_button = ttk.Button(button_frame, text="Beenden", command=root.quit)
    quit_button.grid(row=0, column=2, padx=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
