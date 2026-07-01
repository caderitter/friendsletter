import logging
from helpers import log_in_to_imap_and_listen, parse_message
from db import friend_exists, init_db

logger = logging.getLogger(__name__)


def handle_new_message(raw_email_bytes):
    parsed = parse_message(raw_email_bytes)
    from_address = parsed["from"]
    subject = parsed["subject"]
    body_plain = parsed["body_plain"]
    body_html = parsed["body_html"]

    logger.info("New email received:")
    logger.info("From: %s", from_address)
    logger.info("Subject: %s", subject)
    logger.info("Body (plain text):\n%s", body_plain)
    logger.info("Body (HTML):\n%s", body_html)

    if not friend_exists(from_address):
        logger.warning("The sender %s is not in your friends list.", from_address)
        return


def main(args=None):
    logging.basicConfig(
        filename="friendslist.log", level=args.log_level if args else logging.INFO
    )
    init_db()
    log_in_to_imap_and_listen(handle_new_message)


if __name__ == "__main__":
    main()
