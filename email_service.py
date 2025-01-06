from email import encoders
from email.mime.base import MIMEBase
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import FROM_EMAIL, SMTP_USER, SMTP_PASS, SMTP_SERVER, SMTP_PORT

def send_email_html(
    subject: str, 
    to_email: str, 
    html_content: str, 
    cc_email: str = None,
    attachments: list = None
):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    if cc_email:
        msg['Cc'] = cc_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    if attachments:
        for attachment in attachments:
            with open(attachment, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            name = attachment.split("/")[-1]
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {name}",
            )
            msg.attach(part)
            

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(FROM_EMAIL, [to_email] + ([cc_email] if cc_email else []), msg.as_string())
    server.quit()