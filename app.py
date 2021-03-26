import pandas as pd
import hashlib
import os
import datetime as dt
import numpy as np
import pprint
import re
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def do_transaction(customer_data, login_id, trans_hist):
    transaction_type = int(input("[1] Deposit\n[2] Withdraw\n[3] Enquiry\nPlease select anyone of the above options"))
    print(transaction_type)
    if (transaction_type == 1):
        amt = int(input("Enter the amount you want to deposit: "))
        customer_data[login_id]["balance"] = customer_data[login_id]["balance"] + amt
        print("updated balance : ", customer_data[login_id]["balance"])
        np.save("customer_data.npy", customer_data)
        trans_hist["date_time"].append(dt.datetime.utcnow().timestamp())
        trans_hist["balance"].append(customer_data[login_id]["balance"])
        trans_hist["transaction_type"].append("deposit")
    elif (transaction_type == 2):
        amt = int(input("Enter the amount you want to withdraw: "))
        if amt > customer_data[login_id]["balance"]:
            print("amount withdrawn is greater than the current balance in account\ncurrent balance : ",
                  customer_data[login_id]["balance"])
        else:
            customer_data[login_id]["balance"] = customer_data[login_id]["balance"] - amt
            print("updated balance : ", customer_data[login_id]["balance"])
            np.save("customer_data.npy", customer_data)
            trans_hist["date_time"].append(dt.datetime.utcnow().timestamp())
            trans_hist["balance"].append(customer_data[login_id]["balance"])
            trans_hist["transaction_type"].append("withdrawl")
    elif (transaction_type == 3):
        print("Current Balance : ", customer_data[login_id]["balance"])


def load_transaction_history(login_id):
    foldername = "transaction_history"
    filename = hashlib.sha256(login_id.encode("utf8")).hexdigest() + ".csv"
    if os.path.exists(os.path.join(foldername, filename)):
        return pd.read_csv(os.path.join(foldername, filename), index_col=False).to_dict("list")
    else:
        return {
            "date_time": [],
            "balance": [],
            "transaction_type": []
        }


def save_transaction_history(trans_hist, login_id):
    foldername = "transaction_history"
    filename = hashlib.sha256(login_id.encode("utf8")).hexdigest() + ".csv"
    pd.DataFrame(data=trans_hist).to_csv(os.path.join(foldername, filename), index=False)


def view_download_transaction(customer_data, login_id, manager_id):
    print("please enter the date time period you want to see transaction")
    fr_yy = int(input("from year: "))
    fr_mm = int(input("from month: "))
    fr_dd = int(input("from day: "))
    to_yy = int(input("to year: "))
    to_mm = int(input("to month: "))
    to_dd = int(input("to day: "))
    fr_date = dt.datetime(year=fr_yy, month=fr_mm, day=fr_dd)
    to_date = dt.datetime(year=to_yy, month=to_mm, day=to_dd)
    trans_hist = load_transaction_history(login_id)
    time_trans_hist = {
        "date_time": [],
        "balance": [],
        "transaction_type": []
    }
    index = 0
    for timestamp in trans_hist["date_time"]:
        if timestamp >= fr_date.timestamp() and timestamp <= to_date.timestamp():
            time_trans_hist["date_time"].append(timestamp)
            time_trans_hist["balance"].append(trans_hist["balance"][index])
            time_trans_hist["transaction_type"].append(trans_hist["transaction_type"][index])
        index += 1
    print("transactions for time period ", fr_date, " to ", to_date)
    trans_df = pd.DataFrame(data=time_trans_hist)
    print(trans_df)
    to_mail = input("Do you want to mail yourself this transaction: ")
    if to_mail == "y" or to_mail == "Y":
        mail_transaction(trans_df, login_id, fr_date, to_date, manager_id)


def mail_transaction(trans_df, login_id, fr_date, to_date, manager_id):
    subject = "Spark18 bank transaction history for " + login_id
    body = "Please find attached transaction history for the billing period :" + str(fr_date) + " to " + str(to_date)
    sender_email = "spark18test@gmail.com"
    receiver_email = manager_id
    password = "spark_18@ankita"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    foldername = "transaction_history"
    filename = hashlib.sha256(login_id.encode("utf8")).hexdigest() + "transaction-history-" + str(fr_date.timestamp()) + \
               str(to_date.timestamp()) + ".csv"
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


if __name__ == '__main__':
    customer_data = np.load("customer_data.npy", allow_pickle=True).tolist()
    pprint.pprint(customer_data)

    option = int(input("[1] Login\n[2] Register\n[3] Login as Manager\nPlease select anyone of the above options: "))
    if option == 1:
        login_id = input("Please enter your login id : ")
        login_pwd = input("please enter your password : ")
        if (login_id in customer_data) and (
                customer_data[login_id]["pwd"] == hashlib.sha256(login_pwd.encode("utf8")).hexdigest()):
            print("loggedIn")
            trans_hist = load_transaction_history(login_id)
            do_transaction(customer_data, login_id, trans_hist)
            save_transaction_history(trans_hist, login_id)
        else:
            print("Invalid UserId or Password")
    elif option == 2:
        login_id = input("Please enter your email id : ")
        login_pwd_0 = input("please enter your password : ")
        login_pwd_1 = input("confirm password : ")
        if login_pwd_0 == login_pwd_1:
            customer_data[login_id] = {
                "balance": 0.0,
                "pwd": hashlib.sha256(login_pwd_0.encode("utf8")).hexdigest()
            }
            print("You have been registered, current balance : ", customer_data[login_id]["balance"])
            np.save("customer_data.npy", customer_data)
        else:
            print("Passwords don't match")
    elif option == 3:
        manager_id = input("Please enter manager id: ")
        manager_pwd = input("Please enter manager password: ")

        if (manager_id == "spark18manager@gmail.com") and (
                hashlib.sha256(manager_pwd.encode("utf8")).hexdigest() == customer_data[manager_id]["pwd"]):

            key_index = []
            index = 0
            for email_id in customer_data:
                if email_id != manager_id:
                    print(index, email_id)
                    key_index.append(email_id)
                    index += 1
            selection = input(
                "please select the indexes of customers you want to view transactions for, separated by spaces: ")
            selected_indices = np.unique(re.findall(r"\b\d+\b", selection))
            print("you have selected the following valid indices : ")
            for index in selected_indices:
                if int(index) < len(key_index) and int(index) > -1:
                    print(index, key_index[int(index)])
                    view_download_transaction(customer_data, key_index[int(index)], manager_id)
        else:
            print("Invalid Manager Password")
