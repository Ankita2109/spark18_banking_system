import pandas as pd
import numpy as np
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import os
import datetime as dt
import json

with open("config.json", "r") as config_file :
    config = json.load(config_file)


def do_transaction(customer_data, login_id, trans_hist):
    transaction_type = input('''[1] Deposit
[2] Withdraw
[3] Enquiry
[4] Quit doing transaction
Please select anyone of the above options : ''')
    while transaction_type != "4":
        if (transaction_type == "1"):
            try:
                amt = float(input("Enter the amount you want to deposit: "))
                if amt < 0:
                    print("Amount should be a positive float value")
                else:
                    customer_data[login_id]["balance"] = \
                    customer_data[login_id][
                        "balance"] + amt
                    print("updated balance : ",
                          customer_data[login_id]["balance"])
                    np.save("customer_data.npy", customer_data)
                    current_datetime = dt.datetime.utcnow()
                    trans_hist["date_time"].append(current_datetime.timestamp())
                    trans_hist["balance"].append(
                        customer_data[login_id]["balance"])
                    trans_hist["transaction_type"].append("deposit")
                    d = {
                        "date_time": [current_datetime],
                        "balance": [customer_data[login_id]["balance"]]
                    }
                    print("Sending email to ", login_id)
                    subject = "Spark18 bank transaction done by " + login_id
                    body = "Please find attached transaction done on " + str(
                        current_datetime) + ", deposit: " + str(amt)
                    mail_transaction(pd.DataFrame(data = d), login_id, subject,
                                     body, login_id)
            except:
                print("Amount should be a positive float value")
        elif (transaction_type == "2"):
            try:
                amt = float(input("Enter the amount you want to withdraw: "))
                if amt < 0:
                    print("Enter a valid positive float value")
                else:
                    if amt > customer_data[login_id]["balance"]:
                        print(
                            "amount withdrawn is greater than the current balance in account\ncurrent balance : ",
                            customer_data[login_id]["balance"])
                    else:
                        customer_data[login_id]["balance"] = \
                        customer_data[login_id][
                            "balance"] - amt
                        print("updated balance : ",
                              customer_data[login_id]["balance"])
                        np.save("customer_data.npy", customer_data)
                        current_datetime = dt.datetime.utcnow()
                        trans_hist["date_time"].append(
                            current_datetime.timestamp())
                        trans_hist["balance"].append(
                            customer_data[login_id]["balance"])
                        trans_hist["transaction_type"].append("withdrawl")
                        d = {
                            "date_time": [current_datetime],
                            "balance": [customer_data[login_id]["balance"]]
                        }
                        print("Sending email to ", login_id)
                        subject = "Spark18 bank transaction done by " + login_id
                        body = "Please find attached transaction done on " + str(
                            current_datetime) + ", withdrawl: " + str(amt)
                        mail_transaction(pd.DataFrame(data=d), login_id,
                                         subject,
                                         body, login_id)
            except:
                print("Enter a valid positive float value")
        elif (transaction_type == "3"):
            print("Current Balance : ", customer_data[login_id]["balance"])
        elif (transaction_type == "4"):
            print("Don't want to do any transaction")
        else:
            print("Please enter a valid input")
        transaction_type = input('''[1] Deposit
[2] Withdraw
[3] Enquiry
[4] Quit doing transaction
Please select anyone of the above options : ''')


def mail_transaction(trans_df, login_id, subject, body, receiver_email):
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


