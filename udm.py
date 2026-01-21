from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.popup import Popup

import psutil
import pandas as pd
from datetime import datetime
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image as PILImage

# ==========================
# SETTINGS
# ==========================
file_name = "activity_log.csv"
PASSWORD = "1234"   # Mobile App Login Password

# CSV Setup
try:
    df = pd.read_csv(file_name)
except FileNotFoundError:
    df = pd.DataFrame(columns=["DateTime", "AppName"])
    df.to_csv(file_name, index=False)

# ==========================
# Activity Tracker Thread
# ==========================
def track_activity():
    global df
    while True:
        for proc in psutil.process_iter(['name']):
            app_name = proc.info['name']
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([[current_time, app_name]], columns=["DateTime", "AppName"])
            df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(file_name, index=False)
        threading.Event().wait(30)  # প্রতি ৩০ সেকেন্ডে আপডেট

tracker_thread = threading.Thread(target=track_activity, daemon=True)
tracker_thread.start()

# ==========================
# Duration Calculation
# ==========================
def calculate_duration():
    global df
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    duration_dict = {}
    prev_app = None
    prev_time = None
    for _, row in df.iterrows():
        app = row['AppName']
        time_now = row['DateTime']
        if prev_app == app:
            delta = (time_now - prev_time).total_seconds()
            duration_dict[app] = duration_dict.get(app, 0) + delta
        prev_app = app
        prev_time = time_now
    for app in duration_dict:
        duration_dict[app] = round(duration_dict[app]/60, 2)  # Minutes
    return duration_dict

# ==========================
# Mobile App GUI
# ==========================
class DashboardApp(App):
    def build(self):
        self.root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.show_login()
        return self.root_layout

    # --------------------------
    # Login Screen
    # --------------------------
    def show_login(self):
        self.root_layout.clear_widgets()
        login_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        login_layout.add_widget(Label(text="Enter Password", font_size=24))
        self.pwd_input = TextInput(password=True, multiline=False, font_size=20)
        login_layout.add_widget(self.pwd_input)

        login_btn = Button(text="Login", size_hint=(1, 0.3))
        login_btn.bind(on_release=self.check_password)
        login_layout.add_widget(login_btn)

        self.root_layout.add_widget(login_layout)

    def check_password(self, instance):
        if self.pwd_input.text == PASSWORD:
            self.show_dashboard()
        else:
            popup = Popup(title="Error", content=Label(text="Wrong Password!"), size_hint=(0.6,0.3))
            popup.open()

    # --------------------------
    # Dashboard Screen
    # --------------------------
    def show_dashboard(self):
        self.root_layout.clear_widgets()

        # Logo + Name
        logo = Image(source='logo.png', size_hint=(1, 0.3))
        self.root_layout.add_widget(logo)
        self.root_layout.add_widget(Label(text="Nazmul Haque Boss", font_size=24, bold=True, size_hint=(1, 0.1)))

        # Scrollable Activity List
        scroll = ScrollView(size_hint=(1, 0.5))
        self.activity_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.activity_layout.bind(minimum_height=self.activity_layout.setter('height'))
        scroll.add_widget(self.activity_layout)
        self.root_layout.add_widget(scroll)

        # Buttons: Refresh + Show Graph
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        refresh_btn = Button(text="Refresh")
        refresh_btn.bind(on_release=lambda x: self.load_activity())
        graph_btn = Button(text="Show Graph")
        graph_btn.bind(on_release=lambda x: self.show_graph())
        btn_layout.add_widget(refresh_btn)
        btn_layout.add_widget(graph_btn)
        self.root_layout.add_widget(btn_layout)

        # Load initial activity
        self.load_activity()

    # --------------------------
    # Load Activity into ScrollView
    # --------------------------
    def load_activity(self):
        self.activity_layout.clear_widgets()
        global df
        df = pd.read_csv(file_name)
        last_50 = df.tail(50)  # Show last 50 activities
        for _, row in last_50.iterrows():
            self.activity_layout.add_widget(Label(text=f"{row['DateTime']} - {row['AppName']}", size_hint_y=None, height=30))

    # --------------------------
    # Show Graph
    # --------------------------
    def show_graph(self):
        durations = calculate_duration()
        if not durations:
            popup = Popup(title="Info", content=Label(text="No data to display!"), size_hint=(0.6,0.3))
            popup.open()
            return
        apps = list(durations.keys())
        minutes = list(durations.values())
        plt.figure(figsize=(8,6))
        bars = plt.barh(apps, minutes, color='skyblue')
        plt.xlabel("Minutes")
        plt.ylabel("Applications")
        plt.title(f"Application Usage (Date: {datetime.now().strftime('%d %b %Y')})")
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                     f'{width} min', va='center')
        plt.tight_layout()
        plt.show()

# Run App
DashboardApp().run()
