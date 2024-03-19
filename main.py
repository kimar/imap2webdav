import os
import time
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
allowed_senders = (config.get('ALLOWED_SENDERS') or "").split(',') or []
imap_use_idle = config.get('IMAP_USE_IDLE', 'false').lower() == 'true'
imap_idle_timeout = 60

# WebDAV configuration
webdav_url = config.get('WEBDAV_URL')
webdav_user = config.get('WEBDAV_USER')
webdav_pass = config.get('WEBDAV_PASS')


def start():
    print("Starting up...")

    def start_scheduler():
        schedule.every().minute.do(fetch_and_parse_messages)
        print("Scheduler started.")

        while True:
            schedule.run_pending()
            time.sleep(1)

    def move_to_trash(msg):
        mailbox.move(msg.uid, 'Trash')
        print(f"Moved email {msg.uid} to Trash.")

    def fetch_and_parse_messages():
        # Fetch all emails in the INBOX
        for msg in mailbox.fetch(imap_tools.A(all=True)):
            print(f"Processing email {msg.uid}, from {msg.from_}...")

            # Check if sender is allowed
            if allowed_senders and msg.from_ not in allowed_senders:
                print(f"Sender {msg.from_} not allowed.")
                move_to_trash(msg)
                continue

            # Check if email has attachments
            if not msg.attachments:
                print("No attachments found.")
                move_to_trash(msg)

            # Process attachments
            for att in msg.attachments:
                file_name = att.filename
                file_path = os.path.join("/tmp", file_name)
                # Save attachment to a temporary file
                with open(file_path, 'wb') as f:
                    f.write(att.payload)

                # Upload file to WebDAV
                with open(file_path, 'rb') as f:
                    response = requests.put(
                        webdav_url + '/' +
                        f"{msg.uid}_{file_name}",
                        data=f,
                        auth=HTTPBasicAuth(webdav_user, webdav_pass)
                    )
                    if response.status_code in [200, 201]:
                        print(f"Uploaded {file_name} successfully.")
                        move_to_trash(msg)
                    else:
                        print(
                            f"Failed to upload {file_name}. Status code: {response.status_code}")

                # Clean up: remove file from local system
                os.remove(file_path)

    # Connect to IMAP server
    with imap_tools.MailBox(imap_host).login(imap_user, imap_pass, initial_folder='INBOX') as mailbox:
        if imap_use_idle:
            print(f'Using IDLE with timeout of {imap_idle_timeout} seconds.')
            responses = mailbox.idle.wait(timeout=imap_idle_timeout)
            if responses:
                fetch_and_parse_messages()
            else:
                print("No new emails.")
                start()
        else:
            print("Not using IDLE. Scheduling a fetch.")
            start_scheduler()

    print("Done.")


if __name__ == '__main__':
    start()
