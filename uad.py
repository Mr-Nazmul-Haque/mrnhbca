import psutil
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from tkinter import Label

# Tkinter Root
root = tk.Tk()
root.title("Ultimate Activity Dashboard")
root.geometry("1000x900")

# ========================
# Name Add
# ========================
name_label = Label(root, text="Mr. Nazmul Boss", font=("Arial", 22, "bold"))
name_label.pack(pady=5)


# ========================
# Logo Add
# ========================
img = Image.open("img/chatgpt.png")     # logo.png ফাইল path
img = img.resize((400, 500))     # Logo size adjust
logo_image = ImageTk.PhotoImage(img)

logo_label = Label(root, image=logo_image)
logo_label.pack(pady=5)


file_name = "activity_log.csv"
PASSWORD = "mr.nhb.ca"  # আপনি চাইলে নিজে পরিবর্তন করতে পারবেন

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
        time.sleep(30)

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

# গ্রাফ দেখানোর ফাংশন
def show_graph(durations):
    if not durations:
        messagebox.showinfo("Info", "No data to display in chart.")
        return

    apps = list(durations.keys())
    minutes = list(durations.values())

    plt.figure(figsize=(10,6))
    bars = plt.barh(apps, minutes, color='skyblue')

    # X-axis label with Date + Month
    plt.xlabel("Minutes")
    plt.ylabel("Applications")
    plt.title(f"Application Usage (Date: {datetime.now().strftime('%d %b %Y')})")

    # Show value at the end of each bar
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                 f'{width} min', va='center')

    plt.tight_layout()
    plt.show()

# GUI Dashboard
def show_dashboard():
    # Password Protection
    pwd = simpledialog.askstring("Password", "Enter Dashboard Password:", show="*")
    if pwd != PASSWORD:
        messagebox.showerror("Error", "Wrong Password! Exiting...")
        return

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
            summary_text = "Summary (App: Minutes)\n"
            for app, mins in durations.items():
                summary_text += f"{app}: {mins} min\n"
            summary_label.config(text=summary_text)

            # Show Graph
            show_graph(durations)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("Ultimate Activity Dashboard")
    root.geometry("750x500")

    top_frame = tk.Frame(root)
    top_frame.pack(pady=10)

    tk.Label(top_frame, text="Filter Date (YYYY-MM-DD):").pack(side=tk.LEFT)
    date_entry = tk.Entry(top_frame)
    date_entry.pack(side=tk.LEFT, padx=5)

    btn_refresh = tk.Button(top_frame, text="Refresh & Show Graph", command=load_data)
    btn_refresh.pack(side=tk.LEFT, padx=5)

    tree = ttk.Treeview(root, columns=("DateTime", "AppName"), show="headings")
    tree.heading("DateTime", text="Date & Time")
    tree.heading("AppName", text="Application Name")
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    summary_label = tk.Label(root, text="Summary", justify=tk.LEFT, anchor="w")
    summary_label.pack(fill=tk.BOTH, padx=10)

    load_data()
    root.mainloop()

# Threading দিয়ে tracker চালানো (GUI এর সাথে parallel)
tracker_thread = threading.Thread(target=track_activity, daemon=True)
tracker_thread.start()

# GUI চালানো
show_dashboard()
