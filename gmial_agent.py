import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# Gmail API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def gmail_authenticate():
    """Authenticate the user and return Gmail API service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_recent_emails(service, max_results=10):
    """List recent emails from Inbox."""
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    emails_list = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")
        snippet = msg_data.get('snippet', "")
        unread = 'UNREAD' in msg_data.get('labelIds', [])
        emails_list.append({
            "id": msg['id'],
            "from": sender,
            "subject": subject,
            "snippet": snippet,
            "unread": unread
        })
    return emails_list

def list_inbox(service, max_results=10):
    """List inbox messages with basic info."""
    return list_recent_emails(service, max_results)

def search_emails(service, query):
    """Search emails by query."""
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    email_list = []

    if not messages:
        return []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
        email_list.append({"id": msg['id'], "from": sender, "subject": subject})
    return email_list

def read_email(service, msg_id):
    """Read full content of an email."""
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']
    body = ""

    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    body += base64.urlsafe_b64decode(data).decode()
    else:
        data = payload['body'].get('data')
        if data:
            body = base64.urlsafe_b64decode(data).decode()

    return body.strip()

def send_email(service, to, subject, message_text):
    """Send an email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw_message}
    sent = service.users().messages().send(userId='me', body=body).execute()
    return sent['id']
