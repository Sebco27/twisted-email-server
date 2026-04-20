import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description='SMTP Client', add_help=False)
    parser.add_argument("-h", "--server", required=True, help="SMTP Server")
    parser.add_argument("-c", "--csv", required=True, help="CSV eMails File")
    parser.add_argument("-m", "--message", required=True, help="Message File")
    parser.add_argument("--help", action="help", help="Show help")
    args = parser.parse_args()
    # sendEmail(args.csv, args.message)

def personalizeMessage(recipient, messageFile):
    with open(messageFile, "r") as f:
        template = f.read()
    try:
        message = template.format(name=recipient["Name"])
    except KeyError:
        message = template
    return message

def sendEmail(csvEmailsFile, messageFile):
    with open(csvEmailsFile) as csvFile:
        recipients = csv.DictReader(csvFile)
        for recipient in recipients:
            message = personalizeMessage(recipient, messageFile)
            # TODO

if __name__ == "__main__":
    main()
