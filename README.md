# Mailstriker
This is my first project as cybersecurity student. this is not homework or not assignment i was just exploring and i found this as simple that i can do. done in first week of first semester
# 🌀 MAILSTRIKE – Email-Based Remote Control & Screenshot Tool (Windows)

**MAILSTRIKE** is a Python-based remote control utility that allows you to securely control **your own Windows system** using email commands.  
It can display popup messages, capture screenshots, and perform a graceful shutdown — all triggered via Gmail.

> ⚠️ **Educational & Personal Use Only**  
> This project is intended for learning, automation, and personal system control.  
> Do **NOT** use this on systems you do not own or have explicit permission to access.

---

## ✨ Features

- 📬 Email-based remote command execution
- 🖥️ Capture and receive live screenshots via email
- 🔔 Display native Windows popup messages
- ⏻ Graceful system shutdown with delay
- 🔐 Sender email verification for basic security
- 🪟 Designed specifically for **Windows OS**

---

## 📌 Supported Commands (Email Subject)

| Subject        | Action |
|---------------|--------|
| `check`        | Shows a popup with the email body message |
| `show screen`  | Takes a screenshot and emails it back |
| `shutdown`     | Initiates a delayed system shutdown |

---

## 🛠️ Requirements

- **Windows OS**
- **Python 3.8+**
- Gmail account with **App Password enabled**
- Internet connection

### Python Libraries Used
- `imaplib`
- `smtplib`
- `email`
- `Pillow`
- `ctypes`
- `os`
- `time`



⚙️ Configuration

Edit the USER CONFIGURATION section in the script:

YOUR_EMAIL   = "your_email@gmail.com"
APP_PASSWORD = "your_gmail_app_password"
SENDER_EMAIL = "authorized_sender@gmail.com"


Use a Gmail App Password, not your real Gmail password

Only emails from SENDER_EMAIL will be accepted as commands

🚀 How It Works

The script continuously checks your Gmail inbox

Reads unseen emails

Verifies sender email

Executes actions based on the email subject

Sends responses (like screenshots) back via SMTP

🧠 Security Notes

Uses Gmail App Password (safer than raw credentials)

Sender email validation prevents random command execution

Designed for personal device control only

Not stealthy or hidden by default

🔒 For advanced security, consider:

Encrypted commands

Token-based authentication

Running as a Windows service

Using IMAP labels instead of inbox scanning

📂 Project Structure
MAILSTRIKE/
│
├── mailstrike.py
├── README.md

🧪 Tested On

Windows 10

Windows 11

Python 3.10+

🧑‍💻 Author

shyclone
Cybersecurity Student
December 2025

Install Pillow if not already installed:
```bash
pip install pillow
