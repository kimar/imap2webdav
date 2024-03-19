# imap2webdav

## Introduction

I'm using this code to fetch mails from an IMAP inbox and put them into my Nextcloud via WebDav. Typically for emails originating from my scanner.

## Configuration

To configure the script you can use environment variables or an `.env` file using the contents below:

```bash
# IMAP
IMAP_HOST=mail.example.com
IMAP_USER=email@example.com
IMAP_PASS=pa55w0rd
IMAP_USE_IDLE=true
ALLOWED_SENDERS=sender1@example.com,sender2@example.com # if empty then all senders are allowed

# WebDAV
WEBDAV_URL=https://cloud.example.com/remote.php/dav/files/USER/FOLDER # omit trailing slash (will be appended by script)
WEBDAV_USER=USER
WEBDAV_PASS=sup3rs3cr3t
```

## How to run

You could run this code locally by using `pipenv`as follows:

```bash
$ pipenv run python -u main.py
```

Or via docker:

```bash
$ docker run -it ghcr.io/kimar/imap2webdav:latest
```

## License

See [LICENSE.md](LICENSE.md).
