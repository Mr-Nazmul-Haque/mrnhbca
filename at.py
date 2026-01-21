import psutil
import time
import pandas as pd
from datetime import datetime

# ডাটাবেস হিসেবে CSV ফাইল
file_name = "activity_log.csv"

# যদি ফাইল না থাকে, create করে column বানানো
try:
    df = pd.read_csv(file_name)
except FileNotFoundError:
    df = pd.DataFrame(columns=["DateTime", "AppName"])
    df.to_csv(file_name, index=False)

print("Activity Tracker চালু হয়েছে... (Ctrl+C দিয়ে বন্ধ করতে পারেন)")

while True:
    for proc in psutil.process_iter(['name']):
        app_name = proc.info['name']
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([[current_time, app_name]], columns=["DateTime", "AppName"])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(file_name, index=False)
    time.sleep(30)  # প্রতি ৩০ সেকেন্ডে ট্র্যাক
