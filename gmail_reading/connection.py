import imaplib
import os
from typing import Optional

import typer
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

USER_EMAIL_ADDRESS = os.environ.get("USER_EMAIL_ADDRESS", "")
USER_PASSWORD = os.environ.get("USER_PASSWORD", "")
IMAP_URL = "imap.gmail.com"
IMAP_PORT = 993


def create_imap_conn() -> Optional[imaplib.IMAP4_SSL]:
    if not USER_EMAIL_ADDRESS or not USER_PASSWORD:
        raise Exception("Credentials must not be empty...")

    try:
        # this is done to make SSL connection with GMAIL
        con = imaplib.IMAP4_SSL(IMAP_URL, port=IMAP_PORT)

        # logging the user in
        con.login(USER_EMAIL_ADDRESS, USER_PASSWORD)
        return con
    except Exception as e:
        typer.echo(f"Connection error: {e}")
        typer.echo(
            "Try enabling IMAP, veryfing the right credentials or allowing less secure apps in your gmail account"
        )
        return None


def shut_down_conn(con: imaplib.IMAP4_SSL) -> None:
    con.close()
    con.logout()
