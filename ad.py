import psutil
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

file_name = "activity_log.csv"

# CSV তৈরি (যদি না থাকে)
try:
    df = pd.read_csv(file_name)
except FileNotFoundError:
    df = pd.DataFrame(columns=["DateTime", "AppName"])
    df.to_csv(file_name, index=False)

# Activity ট্র্যাকিং ফাংশন
def track_activity():
    global df
    while True:
        for proc in psutil.process_iter(['name']):
            app_name = proc.info['name']
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([[current_time, app_name]], columns=["DateTime", "AppName"])
            df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(file_name, index=False)
        time.sleep(30)  # প্রতি ৩০ সেকেন্ডে আপডেট

# GUI Dashboard
def show_dashboard():
    def load_data():
        try:
            df_gui = pd.read_csv(file_name)
            for i in tree.get_children():
                tree.delete(i)
            for index, row in df_gui.iterrows():
                tree.insert("", "end", values=(row["DateTime"], row["AppName"]))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("Activity Dashboard")
    root.geometry("600x400")

    tree = ttk.Treeview(root, columns=("DateTime", "AppName"), show="headings")
    tree.heading("DateTime", text="Date & Time")
    tree.heading("AppName", text="Application Name")
    tree.pack(fill=tk.BOTH, expand=True)

    btn_refresh = tk.Button(root, text="Refresh Data", command=load_data)
    btn_refresh.pack(pady=10)

    load_data()
    root.mainloop()

# Threading দিয়ে tracker চালানো (GUI এর সাথে parallel)
tracker_thread = threading.Thread(target=track_activity, daemon=True)
tracker_thread.start()

# GUI চালানো
show_dashboard()