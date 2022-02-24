from cgitb import html
import datetime as dt
import email
from email.message import Message
from email.iterators import _structure
from genericpath import exists
import imaplib
from typing import Optional, Union
from pathlib import Path

import pandas as pd
import typer

from gmail_reading import BASE_DIR

ATTACH_PATH = BASE_DIR / "attachments"
ATTACH_PATH.mkdir(exist_ok=True)


def raw_date_to_dt(raw_date: str) -> Optional[dt.datetime]:
    date_tuple = email.utils.parsedate_tz(raw_date)
    if date_tuple:
        return dt.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
    return None


def decode_msg_parts(msg_part):
    if not msg_part:
        return ""
    if msg_part["content-transfer-encoding"] != "7bit":
        return msg_part.get_payload().decode(msg_part["content-transfer-encoding"])
    return msg_part.get_payload()


def get_msg_body(email_msg: Message) -> bytes:
    if email_msg.is_multipart():
        return get_msg_body(email_msg.get_payload(0))
    else:
        return email_msg.get_payload(None, True)


def get_html_body(email_msg: Message) -> bytes:
    if email_msg.is_multipart():
        try:
            html = email_msg.get_payload(1)
        except ValueError:
            return b""

        if html.get_content_subtype() != "html":
            return b""
        return get_html_body(html)
    else:
        return email_msg.get_payload(None, True)


def get_attachments(msg: Message, folder_name: Path) -> None:
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue
        file_name = part.get_filename()

        if bool(file_name):
            folder_name.mkdir(exist_ok=True, parents=True)
            file_path = folder_name / file_name
            with open(file_path, "wb") as f:
                f.write(part.get_payload(decode=True))


def fetch_msgs_from_user(user_mail: str, con: imaplib.IMAP4_SSL):
    all_msg_data = {
        "text_msg": [],
        "html_msg": [],
        "sender": [],
        "receiver": [],
        "date": [],
        "title": [],
        "attachments": [],
    }

    # calling function to check for email under this label
    con.select("Inbox")

    # fetching emails from user
    _, result_bytes = con.search(None, "FROM", '"{}"'.format(user_mail))

    typer.echo(f"Response returned {len(result_bytes[0].split())} results")
    if not len(result_bytes[0].split()):
        return

    with typer.progressbar(result_bytes[0].split(), label="Fetching mails") as progress:
        for num in progress:
            res_type, msg_data = con.fetch(num, "(RFC822)")

            if res_type != "OK":
                raise Exception(f"Error getting message at {num}")

            email_msg = email.message_from_bytes(msg_data[0][1])
            receiver = email_msg.get("Delivered-To", "")
            raw_date = email_msg.get("Date", "")
            sender = email_msg.get("From", "")
            title = email_msg.get("Subject", "")

            parsed_date = raw_date_to_dt(raw_date) if raw_date else None

            text = get_msg_body(email_msg)
            html = get_html_body(email_msg)

            try:
                all_msg_data["text_msg"].append(text.decode())
            except UnicodeEncodeError as e:
                typer.echo(f"Something went wrong with the body encoding.")

            all_msg_data["html_msg"].append(html)

            all_msg_data["date"].append(parsed_date)
            all_msg_data["sender"].append(sender)
            all_msg_data["receiver"].append(receiver)
            all_msg_data["title"].append(title)

            # Attachements if any
            attach_subfolder = ATTACH_PATH / f"attach_{num.decode()}"
            get_attachments(email_msg, attach_subfolder)
            if attach_subfolder.exists():
                all_msg_data["attachments"].append(attach_subfolder.as_posix())
            else:
                all_msg_data["attachments"].append("")

    df = pd.DataFrame(all_msg_data)
    df.to_csv(BASE_DIR / "mail_fetch_results.csv", index=None)
    typer.echo("Done!")
