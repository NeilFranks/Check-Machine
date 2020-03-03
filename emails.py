from __future__ import print_function
import base64
import email
import json
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import WebDriver

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# This method downloads the attachment and returns the absolute path
def get_attachment(message):

    filePath = ""

    msg_str = base64.urlsafe_b64decode(message["raw"].encode("ASCII"))
    email_message = email.message_from_bytes(msg_str)

    # downloading attachments
    for part in email_message.walk():

        # this part comes from the snipped I don't understand yet...
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue
        fileName = part.get_filename()
        if bool(fileName):
            filePath = os.path.join(".", fileName)
            if not os.path.isfile(filePath):
                fp = open(filePath, "wb")
                fp.write(part.get_payload(decode=True))
                filePath = os.path.abspath(fileName)
                fp.close()

        return filePath


def email_details(service, email_id):
    detailsList = []

    message = (
        service.users().messages().get(userId="me", id=email_id, format="raw").execute()
    )

    msg_str = base64.urlsafe_b64decode(message["raw"].encode("ASCII"))
    mime_msg = email.message_from_bytes(msg_str)
    body = ""
    subject = ""
    try:
        encoded_word_regex = r"=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}="
        charset, encoding, encoded_text = re.match(
            encoded_word_regex, mime_msg["Subject"]
        ).groups()

        subject = mime_msg["Subject"]
        if "=?US-ASCII?Q?" in subject:
            subject = subject.replace("=?US-ASCII?Q?", "")
            subject = subject.replace("?=", "")
            subject = subject.replace("?= ", "")
        elif encoding is "B":
            subject = base64.b64decode(encoded_text)
            subject = subject.decode()
        elif encoding is "Q":
            subject = quopri.decodestring(encoded_text)
            subject = subject.decode()

    except:
        subject = mime_msg["Subject"]

    labels = message.get("labelIds")

    sender = mime_msg["From"]
    date = mime_msg["Date"]

    # sender looks like "name <address@gmail.com>". We just want the first part
    try:
        charset, encoding, text = re.match(
            encoded_word_regex, str(sender.split("<")[0].strip('"'))
        ).groups()
        sender = text
    except:
        sender = sender.split("<")[0].replace('"', "")

    snippet = message.get("snippet")
    detailsList.append(
        {
            "id": email_id,
            "date": date,
            "unread": "UNREAD" in labels,
            "labels": labels,
            "sender": sender,
            "snippet": snippet,
            "subject": subject,
        }
    )

    if email_id == "1709ea9209192157":
        filePath = get_attachment(message)
        WebDriver.download_report(filePath)

    return detailsList


def get_emails(after_time):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)
    # get access to emails
    results = (
        service.users()
        .messages()
        .list(userId="me", q="after:{}".format(after_time))
        .execute()
    )

    for message in results["messages"]:
        details = email_details(service, message["id"])
        # for detail in details:
        #     print(detail)

        # print("\n\n")


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
        print("No labels found.")
    else:
        print("Labels:")
        for label in labels:
            print(label["name"])


if __name__ == "__main__":
    # main()
    get_emails(1583039012)

