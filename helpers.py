import base64
import email
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header, make_header
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from imapclient.imapclient import IMAPClient
from config import config

SCOPES = ["https://mail.google.com/"]


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return creds


def log_in_to_imap_and_listen(handle_message_callback):
    creds = get_credentials()

    with IMAPClient("imap.gmail.com", use_uid=True, ssl=True) as server:
        server.oauth2_login(config["email"], creds.token)
        server.select_folder("INBOX")
        server.idle()
        while True:
            responses = server.idle_check(timeout=30)
            if responses:
                server.idle_done()
                messages = server.search(["UNSEEN"])
                for message_data in server.fetch(messages, ["RFC822"]).values():
                    handle_message_callback(message_data[b"RFC822"])
                server.idle()


def parse_message(raw_email_bytes):
    msg = email.message_from_bytes(raw_email_bytes)

    subject = str(make_header(decode_header(msg["Subject"] or "")))
    from_ = str(make_header(decode_header(msg["From"] or "")))

    body_plain = ""
    body_html = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")

            # skip attachments
            if "attachment" in content_disposition:
                continue

            if content_type == "text/plain" and not body_plain:
                charset = part.get_content_charset() or "utf-8"
                body_plain = part.get_payload(decode=True).decode(
                    charset, errors="replace"
                )

            elif content_type == "text/html" and not body_html:
                charset = part.get_content_charset() or "utf-8"
                body_html = part.get_payload(decode=True).decode(
                    charset, errors="replace"
                )
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True).decode(charset, errors="replace")
        if msg.get_content_type() == "text/html":
            body_html = payload
        else:
            body_plain = payload

    return {
        "subject": subject,
        "from": from_,
        "body_plain": body_plain,
        "body_html": body_html,
    }


def send_email(to_address, subject, body_plain, body_html):
    msg = MIMEMultipart("alternative")
    msg["From"] = config["email"]
    msg["To"] = to_address
    msg["Subject"] = subject

    plain = MIMEText(body_plain, "plain")
    html = MIMEText(body_html, "html")

    msg.attach(plain)
    msg.attach(html)

    creds = get_credentials()
    auth_string = f"user={config['email']}\1auth=Bearer {creds.token}\1\1"
    smtp_conn = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_conn.ehlo()

    smtp_conn.docmd(
        "AUTH", "XOAUTH2 " + base64.b64encode(auth_string.encode()).decode()
    )
    smtp_conn.sendmail(config["email"], [to_address], msg.as_string())
    smtp_conn.quit()
