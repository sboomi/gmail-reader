import typer
from dotenv import find_dotenv, load_dotenv
from pathlib import Path

from gmail_reading.connection import create_imap_conn

from .connection import create_imap_conn, shut_down_conn
from .messages import fetch_msgs_from_user

load_dotenv(find_dotenv())

app = typer.Typer()


@app.callback()
def callback():
    """
    Gmail Reader
    """


@app.command()
def fetch_from_user(user_mail: str):
    """
    Fetch mail from sender's email
    """
    typer.echo(f"Retrieving mails from {user_mail}")
    typer.echo("Logging to your Gmail account...")
    try:
        con = create_imap_conn()
    except Exception:
        typer.echo("Did you configure `USER_EMAIL_ADDRESS` and `USER_PASSWORD` in your env variables?")
        raise typer.Abort()
    if not con:
        typer.echo("Error: couldn't establish IMAP connection with Gmail")
        raise typer.Abort()
    typer.echo("Reading msgs")
    fetch_msgs_from_user(user_mail, con)
    typer.echo("Closing connection...")
    shut_down_conn(con)


@app.command()
def init():
    """
    Asks for credentials
    """
    typer.echo("Gmail IMAP reader")
    env_file = Path(".env")
    if env_file.exists():
        is_overwritten = typer.confirm("Local environment already confirmed. Overwrite?")
        if is_overwritten:
            env_file.unlink()
            typer.echo("Previous .env deleted...")
        else:
            typer.echo("Aborting...")
            raise typer.Exit()
    else:
        typer.echo("Local environment not initialized. Initializing...")

    creds = {}

    creds["USER_EMAIL_ADDRESS"] = typer.prompt("Enter your mail address.")
    creds["USER_PASSWORD"] = typer.prompt("Enter your Gmail password or your 16 character auth code.")
    typer.echo("Saving in local environment...")
    with open(env_file, "w") as env_f:
        for k, v in creds.items():
            env_f.write(f"{k}={v}\n")
    typer.echo("Done!")
    typer.echo("Try the `fetch-from-user` command with a sender mail of your choice!")
