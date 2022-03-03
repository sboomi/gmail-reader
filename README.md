# Gmail reader

**This package needs Poetry version 1.1.12 to work. Don't forget to use `poetry shell` to test the package.**

Get IMAP enabled first, then make sure you can access to your Gmail by either turning down the security or generating a [new app](https://myaccount.google.com/apppasswords)

## Commands

```
  Gmail Reader

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  fetch-from-user  Fetch mail from sender's email
  init             Asks for credentials

```

# TODO

- Implement a widget that takes every mail from a DB and makes stats out of it
- Possibly deletes junkish mails by checking stats
