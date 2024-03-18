import os
import time
from datetime import datetime
from email.policy import default

import imap_tools
import requests
import schedule
from dotenv import dotenv_values
from requests.auth import HTTPBasicAuth

config = {
    **dotenv_values(".env"),
    **os.environ,
}

# IMAP configuration
imap_host = config.get('IMAP_HOST')
imap_user = config.get('IMAP_USER')
imap_pass = config.get('IMAP_PASS')
allowed_senders = config.get('ALLOWED_SENDERS').split(',') or []

# WebDAV configuration
webdav_url = config.get('WEBDAV_URL')
webdav_user = config.get('WEBDAV_USER')
webdav_pass = config.get('WEBDAV_PASS')

# Connect to IMAP server
def fetch_mail():
  def move_to_trash(msg):
      mailbox.move(msg.uid, 'Trash')
      print(f"Moved email {msg.uid} to Trash.")
      
  print("Fetching emails...")
  with imap_tools.MailBox(imap_host).login(imap_user, imap_pass, initial_folder='INBOX') as mailbox:
      
      # Fetch all emails in the INBOX
      for msg in mailbox.fetch(imap_tools.A(all=True)):
          print(f"Processing email {msg.uid}, from {msg.from_}...")

          if allowed_senders.__len__() > 0 and msg.from_ not in allowed_senders:
              print(f"Sender {msg.from_} not allowed.")
              move_to_trash(msg)
              continue

          if msg.attachments.__len__() == 0:
              print("No attachments found.")
              move_to_trash(msg)

          for att in msg.attachments:
              file_name = att.filename
              file_path = os.path.join("/tmp", file_name)
              # Save attachment to a temporary file
              with open(file_path, 'wb') as f:
                  f.write(att.payload)
                  
              # Upload file to WebDAV
              with open(file_path, 'rb') as f:
                  response = requests.put(
                      webdav_url + '/' + f"{datetime.now().strftime('%s')}_{file_name}",
                      data=f,
                      auth=HTTPBasicAuth(webdav_user, webdav_pass)
                  )
                  if response.status_code in [200, 201]:
                      print(f"Uploaded {file_name} successfully.")
                      move_to_trash(msg)
                  else:
                      print(f"Failed to upload {file_name}. Status code: {response.status_code}")
              
              # Clean up: remove file from local system
              os.remove(file_path)
  print("Done.")

schedule.every().minute.do(fetch_mail)

while True:
    schedule.run_pending()
    time.sleep(1)