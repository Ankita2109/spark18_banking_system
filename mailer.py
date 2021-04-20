import hashlib
import json
import os
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class mailer:

    def mail_transaction(self,trans_df, login_id, subject, body, receiver_email):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        sender_email = config["mailbox_id"]
        password = config["mailbox_pwd"]

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        foldername = "transaction_history"
        filename = hashlib.sha256(
            login_id.encode("utf8")).hexdigest() + "transaction-history.csv"
        trans_df.to_csv(os.path.join(foldername, filename), index=False)

        with open(os.path.join(foldername, filename), "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= transaction-history.csv",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

        os.remove(os.path.join(foldername, filename))
        print("Mail has been successfully sent")




