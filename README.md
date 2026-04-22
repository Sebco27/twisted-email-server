# Email System: SMTP & POP3 Servers + SMTP Client

A Python-based email system implementing:
- **SMTP server** (Twisted) – receives messages, validates recipient domains, stores emails per user.
- **POP3 server** (Twisted) – authenticates users, lists/retrieves/deletes messages.
- **SMTP client** – sends personalized bulk emails from a CSV file and a message template.

## Components

### 1. SMTP Server (`smtpserver.py`)
- Accepts emails for allowed domains (loaded from a CSV).
- Stores each email as `email-<timestamp>.eml` in the recipient’s mailbox folder.

```bash
python3 smtpserver.py -d <domains> -s <mail-storage> -p <port>
```

### 2. POP3 Server (`pop3server.py`)
- Authenticates users against `.env` (format: `username=password`).
- Provides standard POP3 commands: `LIST`, `RETR`, `DELE`, `RSET`, `QUIT` (with `sync()`).

```bash
python pop3server.py -s <mail-storage> -p <port>
```

### 3. SMTP Client (`smtpclient.py`)
- Reads recipients from a CSV (columns: `Name`, `Email`).
- Replaces `{name}` placeholders in a text message file.
- Sends emails via the SMTP server (default port 2525).

```bash
python3 smtpclient.py -h <mail-server> -c <csv-file> -m <message-file>
```

### 4. User Authentication (`userservices.py`)
- Loads credentials from `.env`.
- Validates login for POP3.

## Requirements
- Python3
- Twisted (`pip3 install twisted`)

## Limitations (from development)
- No XMPP notifications
- TLS/SSL not fully integrated
- External domain connectivity was not completed due to port configuration issues

---

<div align="center">
    <em>Built with Twisted, argparse, and smtplib</em>
    <br><br>
    <a href="https://www.tec.ac.cr/"><img src="https://www.tec.ac.cr/themes/custom/tecnologico/logo.svg" width="300" style="vertical-align: middle;"/></a>
</div>
