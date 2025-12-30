"""
MAILSTRIKE 🌀 - ULTIMATE Remote Control + Screenshot (Windows)
Created by: shyclone - December 2025

This program:
- Checks Gmail inbox for commands
- Executes actions based on email subject
- Sends screenshots back via email

Commands:
- check       → Shows a popup with message
- show screen → Takes screenshot & emails it
- shutdown    → Gracefully shuts down the PC
"""

# ==================== IMPORTS ====================
import imaplib              # Read emails via IMAP
import email                # Parse email content
import os                   # OS-level commands (shutdown, file delete)
import time                 # Sleep & timestamps
import ctypes               # Windows native popup
import smtplib              # Send emails via SMTP
from PIL import ImageGrab   # Take screenshots (Windows)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import decode_header

# ==================== USER CONFIGURATION ====================
YOUR_EMAIL      = "ac@gmail.com"     # Gmail used to read & send emails
APP_PASSWORD    = "16digidpassword"              # Gmail App Password (NOT normal password)(remove space in between)

SENDER_EMAIL    = "pra@gmail.com"  # Allowed command sender

# SMTP settings for sending emails
SMTP_SERVER     = "smtp.gmail.com"
SMTP_PORT       = 587

CHECK_INTERVAL  = 45   # Check inbox every 45 seconds
SHUTDOWN_DELAY  = 30   # Delay before shutdown (seconds)
# ===========================================================

def decode_text(text):
    """
    Decodes encoded email subject text safely
    """
    if not text:
        return ""
    decoded = decode_header(text)[0]
    try:
        if decoded[1]:
            return decoded[0].decode(decoded[1])
        return decoded[0]
    except:
        return str(decoded[0])

def show_popup(title, message):
    """
    Shows a native Windows popup message box
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Showing popup...")
    ctypes.windll.user32.MessageBoxW(0, message, title, 64)

def graceful_shutdown():
    """
    Initiates a delayed Windows shutdown
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] SHUTDOWN command received")
    os.system(f'shutdown /s /t {SHUTDOWN_DELAY} /c "Remote shutdown by MAILSTRIKE 🌀"')

def send_screenshot_email(user_message=""):
    """
    Takes a screenshot and emails it back to YOU
    """
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Taking screenshot...")

        # Capture full screen
        screenshot = ImageGrab.grab()
        screenshot_path = "screenshot.png"
        screenshot.save(screenshot_path)

        # Build email
        msg = MIMEMultipart()
        msg['From'] = YOUR_EMAIL
        msg['To'] = YOUR_EMAIL
        msg['Subject'] = "MAILSTRIKE 🌀 - Screenshot Captured"

        # Email body
        body_text = f"Screenshot requested at {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        if user_message:
            body_text += f"Your message: {user_message}\n"
        body_text += "Attached: Current screen"

        msg.attach(MIMEText(body_text, 'plain'))

        # Attach screenshot file
        with open(screenshot_path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename="screenshot.png")
            msg.attach(img)

        # Send email using SMTP
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sending screenshot email...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(YOUR_EMAIL, APP_PASSWORD)
        server.sendmail(YOUR_EMAIL, YOUR_EMAIL, msg.as_string())
        server.quit()

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Screenshot sent successfully!")

        # Delete screenshot file after sending
        os.remove(screenshot_path)

        # Optional confirmation popup
        show_popup("MAILSTRIKE 🌀", "Screenshot captured and sent to your email!")

    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Screenshot failed: {e}")
        show_popup("MAILSTRIKE Error", f"Screenshot failed: {str(e)}")

def process_emails():
    """
    Connects to Gmail inbox and processes unseen command emails
    """
    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(YOUR_EMAIL, APP_PASSWORD)
        mail.select("inbox")

        # Search for unread emails
        status, data = mail.search(None, "UNSEEN")
        email_ids = data[0].split()

        for eid in email_ids:
            status, msg_data = mail.fetch(eid, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            from_addr = msg.get("From", "")
            subject_raw = msg.get("Subject", "")
            subject = decode_text(subject_raw).strip().lower()

            # Extract email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        body = payload.decode(errors="ignore").strip()
                        break
            else:
                payload = msg.get_payload(decode=True)
                body = payload.decode(errors="ignore").strip()

            # Security check: only accept commands from allowed sender
            if SENDER_EMAIL.lower() not in from_addr.lower():
                continue

            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Command received: '{subject_raw}'")

            # ===== COMMAND HANDLING =====
            if subject == "check":
                message = body if body else "MAILSTRIKE 🌀 is active!"
                show_popup("MAILSTRIKE 🌀 - Remote Check", message)
                mail.store(eid, '+FLAGS', '\\Seen')

            elif subject == "show screen":
                mail.store(eid, '+FLAGS', '\\Seen')
                send_screenshot_email(body)

            elif subject == "shutdown":
                mail.store(eid, '+FLAGS', '\\Seen')
                mail.close()
                mail.logout()
                graceful_shutdown()
                return "shutdown"

        mail.close()
        mail.logout()

    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: {e}")
        time.sleep(10)

    return None

def main():
    """
    Main loop – keeps checking email every X seconds
    """
    print("MAILSTRIKE 🌀 - ULTIMATE VERSION WITH SCREENSHOT")
    print("Commands (Email Subject):")
    print("   • check")
    print("   • show screen")
    print("   • shutdown\n")

    try:
        while True:
            result = process_emails()
            if result == "shutdown":
                break
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\nMAILSTRIKE 🌀 stopped manually.")

if __name__ == "__main__":
    main()
