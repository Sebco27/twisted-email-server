import argparse
import csv
import smtplib
from email.message import EmailMessage

CLIENT = {
    "email": "sender@example.com",
    "name": "SMTP Client"
}

def main():
    parser = argparse.ArgumentParser(description='SMTP Client', add_help=False)
    parser.add_argument("-h", "--server", required=True, help="SMTP Server")
    parser.add_argument("-c", "--csv", required=True, help="CSV eMails File")
    parser.add_argument("-m", "--message", required=True, help="Message File")
    parser.add_argument("--help", action="help", help="Show help")
    args = parser.parse_args()
    sendEmail(args.server, args.csv, args.message)

def personalizeMessage(recipient, messageFile):
    with open(messageFile, "r") as f:
        template = f.read()
    try:
        message = template.format(name=recipient["Name"])
    except KeyError:
        message = template
    return message

def sendEmail(smtpServer, csvEmailsFile, messageFile):
    with open(csvEmailsFile) as csvFile:
        recipients = csv.DictReader(csvFile)
        with smtplib.SMTP(smtpServer, 2525, timeout=10) as server:
            for recipient in recipients:
                message = EmailMessage()
                message["From"] = CLIENT["email"]
                message["To"] = recipient["Email"]
                message["Subject"] = "Message from " + CLIENT["name"]
                message.set_content(personalizeMessage(recipient, messageFile))
                try:
                    server.send_message(message)
                except:
                    print(f"Rejecting mail to {recipient["Email"]}")

if __name__ == "__main__":
    main()
