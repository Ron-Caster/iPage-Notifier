import imaplib
import email
from email.header import decode_header
import csv
import time  # Import time module
from groq_client import get_groq_response  # Import get_groq_response from groq_client
from tts import read_aloud  # Import read_aloud from tts_script

def read_credentials(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        return next(reader)

def connect_to_mail_server(username, password, imap_server="imap.ipage.com"):
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select("inbox")
    return mail

def list_emails(mail):
    # Search for all emails in the inbox
    status, messages = mail.search(None, "ALL")

    # Convert messages to a list of email IDs
    email_ids = messages[0].split()
    email_ids.reverse()  # Reverse to have the latest email first

    return email_ids

def notify_hari(subject, content):
    system_prompt = "You are an AI Email Assistant, you have to notify your owner Hari when an email is received. The Subject: and Content: of the email will be passed on to you. You have to notify Hari in a short summary that a new mail has arrived. Always start with Hey Hari, followed by the summary. Keep it natural and do not add any symbols and unnecessary raw data to the response. Don't give response like:RE: EPFO KYC Update. If Re: is there in content, notify hari that you got a reply for the Subject which is followed by Re: and summarize the content as usual."
    user_prompt = f"Subject: {subject}\nContent: {content}"
    
    conversation_history = [{"role": "system", "content": system_prompt}]
    summary = get_groq_response(conversation_history, user_prompt)
    
    print(summary)  # Print only the summary
    read_aloud(summary)  # Read the summary aloud

def show_email_content(mail, email_id):
    # Fetch the email by ID
    status, msg_data = mail.fetch(email_id, "(RFC822)")

    # Parse the email content
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            email_subject = subject  # Store subject for notification

            # If the email message is multipart:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        email_content = body  # Store content for notification
            else:
                content_type = msg.get_content_type()
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    email_content = body  # Store content for notification

            notify_hari(email_subject, email_content)  # Notify Hari with the email details

def main():
    username, password = read_credentials('credentials.csv')
    mail = connect_to_mail_server(username, password)

    last_email_id = None

    while True:
        email_ids = list_emails(mail)
        if email_ids:
            current_email_id = email_ids[0]
            if current_email_id != last_email_id:
                show_email_content(mail, current_email_id)
                last_email_id = current_email_id
        time.sleep(10)  # Wait for 30 seconds before fetching emails again


if __name__ == "__main__":
    main()
