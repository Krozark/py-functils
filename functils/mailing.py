# Built-in
import datetime
import os
import re
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import getLogger
from typing import List, Tuple
from urllib.parse import urljoin

# Third-party
import requests

logger = getLogger(__name__)


def _get_attachment_file_nameand_type(path: str, regex: str) -> Tuple[str, str]:
    base_name = os.path.basename(os.path.basename(path))
    name = re.match(regex, base_name).group("name")
    t = name.rsplit(".", 1)[-1]
    return name, t


def send_smtp_mail(
    host: str,
    port: int,
    sender: str,
    receivers: List[str],
    object: str,
    body: str,
    html: str = None,
    attachments: List[Tuple[str, str]] = None,
    attachments_regex: str = None,
    local_hostname: str = None,
    password: str = None,
) -> None:
    logger.debug("Creating SMTP connexion")
    # create smtp connection
    smtp = smtplib.SMTP(
        host=host,
        port=port,
        local_hostname=local_hostname,
    )
    # Login with your email and password
    if password:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender, password)

    logger.info(f"Preparing SMTP e-mail to {receivers}:")
    for receiver in receivers:
        logger.info(f"Sending e-mail to {receiver}.")
        msg_root = MIMEMultipart("related")
        msg_root["Subject"] = object
        msg_root["From"] = sender
        msg_root["To"] = receiver
        msg_root["Date"] = datetime.datetime.now().strftime("%a, %d %b %Y  %H:%M:%S %Z")
        # Set the multipart email preamble attribute value.
        # Please refer https://docs.python.org/3/library/email.message.html to learn more.
        msg_root.preamble = "====================================================="

        # Create a 'alternative' MIMEMultipart object. We will use this object to save plain text format content.
        msg_alternative = MIMEMultipart("alternative")
        msg_root.attach(msg_alternative)

        msg_alternative.attach(MIMEText(body))  # Add text contents
        if html:
            msg_alternative.attach(MIMEText(html, "html"))  # Add html contents

        for attachment_path, attachment_data in attachments or []:  # add attachments
            name, subtype = _get_attachment_file_nameand_type(
                attachment_path, attachments_regex
            )
            attachment = MIMEApplication(attachment_data, name=name, _subtype=subtype)
            attachment["Content-Disposition"] = f'attachment;filename="{name}"'
            msg_root.attach(attachment)

        # logger.debug("Email to send:\n%s", msg_root.as_string())
        smtp.sendmail(from_addr=sender, to_addrs=[receiver], msg=msg_root.as_string())
    smtp.quit()


def send_mailgun_email(
    url: str,
    domain: str,
    key: str,
    sender: str,
    receivers: List[str],
    object: str,
    body: str,
    html: str = None,
    attachments: List[Tuple[str, str]] = None,
    attachments_regex: str = None,
) -> None:
    logger.info(f"Preparing mailgun e-mail to {receivers}:")
    url = urljoin(url, domain + "/messages")
    auth = ("api", key)
    files = [
        (
            "attachment",
            (
                _get_attachment_file_nameand_type(attachment_path, attachments_regex)[
                    0
                ],
                attachment_data,
            ),
        )
        for attachment_path, attachment_data in attachments or []
    ]
    data = {"from": sender, "subject": object, "text": body}
    if html:
        data["html"] = html

    logger.debug(f"mailgun url {url}, with {len(files)} attachment")

    for receiver in receivers:
        logger.info(f"Sending e-mail to {receiver}.")
        response = requests.post(
            url,
            auth=auth,
            files=files,
            data={
                "to": receiver,
                **data,
            },
        )
        if response.status_code != 200:
            logger.error(
                f"Error while querying url '{url}'. {response.status_code}: {response.text}."
            )
            response.raise_for_status()
