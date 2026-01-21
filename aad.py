import psutil
import pandas as pd
from datetime import datetime, timedelta
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

# Duration হিসাব করা
def calculate_duration(filtered_df):
    filtered_df['DateTime'] = pd.to_datetime(filtered_df['DateTime'])
    filtered_df = filtered_df.sort_values('DateTime')
    duration_dict = {}
    prev_app = None
    prev_time = None
    for _, row in filtered_df.iterrows():
        app = row['AppName']
        time_now = row['DateTime']
        if prev_app == app:
            delta = (time_now - prev_time).total_seconds()
            duration_dict[app] = duration_dict.get(app, 0) + delta
        prev_app = app
        prev_time = time_now
    # Duration in minutes
    for app in duration_dict:
        duration_dict[app] = round(duration_dict[app]/60, 2)
    return duration_dict

# GUI Dashboard
def show_dashboard():
    def load_data():
        try:
            df_gui = pd.read_csv(file_name)
            # Date filter
            filter_date = date_entry.get()
            if filter_date:
                df_gui = df_gui[df_gui['DateTime'].str.contains(filter_date)]
            
            # Clear tree
            for i in tree.get_children():
                tree.delete(i)
            
            # Insert filtered data
            for _, row in df_gui.iterrows():
                tree.insert("", "end", values=(row["DateTime"], row["AppName"]))
            
            # Duration summary
            durations = calculate_duration(df_gui)
            summary_text = "Weekly Summary (App: Minutes)\n"
            for app, mins in durations.items():
                summary_text += f"{app}: {mins} min\n"
            summary_label.config(text=summary_text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("Advanced Activity Dashboard")
    root.geometry("700x500")

    top_frame = tk.Frame(root)
    top_frame.pack(pady=10)

    tk.Label(top_frame, text="Filter Date (YYYY-MM-DD):").pack(side=tk.LEFT)
    date_entry = tk.Entry(top_frame)
    date_entry.pack(side=tk.LEFT, padx=5)

    btn_refresh = tk.Button(top_frame, text="Refresh Data", command=load_data)
    btn_refresh.pack(side=tk.LEFT, padx=5)

    tree = ttk.Treeview(root, columns=("DateTime", "AppName"), show="headings")
    tree.heading("DateTime", text="Date & Time")
    tree.heading("AppName", text="Application Name")
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    summary_label = tk.Label(root, text="Weekly Summary", justify=tk.LEFT, anchor="w")
    summary_label.pack(fill=tk.BOTH, padx=10)

    load_data()
    root.mainloop()

# Threading দিয়ে tracker চালানো (GUI এর সাথে parallel)
tracker_thread = threading.Thread(target=track_activity, daemon=True)
tracker_thread.start()

# GUI চালানো
show_dashboard()
