import datetime as dt
import hashlib
import json
import os

import numpy as np
import pandas as pd
from mailer import mailer

class transaction:

    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    def do_transaction(self,customer_data, login_id, trans_hist):
        m = mailer()
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
                        m.mail_transaction(pd.DataFrame(data = d), login_id, subject,
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
                            mailer.mail_transaction(pd.DataFrame(data=d), login_id,
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


    def load_transaction_history(self,login_id):
        foldername = "transaction_history"
        filename = hashlib.sha256(login_id.encode("utf8")).hexdigest() + ".csv"
        if os.path.exists(os.path.join(foldername, filename)):
            return pd.read_csv(os.path.join(foldername, filename),
                               index_col=False).to_dict("list")
        else:
            print(
                "No transaction history for any accounts found, initiating new history ")
            return {
                "date_time": [],
                "balance": [],
                "transaction_type": []
            }


    def save_transaction_history(self,trans_hist, login_id):
        foldername = "transaction_history"
        filename = hashlib.sha256(login_id.encode("utf8")).hexdigest() + ".csv"
        if not os.path.exists(foldername):
            os.mkdir(foldername)
        pd.DataFrame(data=trans_hist).to_csv(os.path.join(foldername, filename),
                                             index=False)


    def view_download_transaction(self,login_id, manager_id):
        self.ml =mailer()
        print("please enter the date time period you want to see transaction")
        valid_date = False
        choice = "y"
        while choice == "y" or choice == "Y":
            try:
                fr_yy = int(input("from year: "))
                fr_mm = int(input("from month: "))
                fr_dd = int(input("from day: "))
                to_yy = int(input("to year: "))
                to_mm = int(input("to month: "))
                to_dd = int(input("to day: "))
                fr_date = dt.datetime(year=fr_yy, month=fr_mm, day=fr_dd)
                to_date = dt.datetime(year=to_yy, month=to_mm, day=to_dd)
                choice = "n"
                valid_date = True
            except:
                choice = input(
                    "This is not a valid date.Do you want to try again , 'y' for yes: ")

        if valid_date:
            trans_hist = self.load_transaction_history(login_id)
            time_trans_hist = {
                "date_time": [],
                "balance": [],
                "transaction_type": []
            }
            index = 0
            for timestamp in trans_hist["date_time"]:
                if timestamp >= fr_date.timestamp() and timestamp <= to_date.timestamp():
                    time_trans_hist["date_time"].append(
                        str(dt.datetime.fromtimestamp(timestamp)))
                    time_trans_hist["balance"].append(trans_hist["balance"][index])
                    time_trans_hist["transaction_type"].append(
                        trans_hist["transaction_type"][index])
                index += 1
            print("transactions for time period ", fr_date, " to ", to_date)
            trans_df = pd.DataFrame(data=time_trans_hist)
            print(trans_df)
            to_mail = input('''[1] Mail yourself this transaction 
    [2] Quit 
    Please select anyone of the above options :  ''')
            while to_mail != "2":
                if to_mail == "1":
                    subject = "Spark18 bank transaction history for " + login_id
                    body = "Please find attached transaction history for the billing period :" + str(
                        fr_date) + " to " + str(to_date)
                    self.ml.mail_transaction(trans_df, login_id, subject, body, manager_id)
                    break
                elif to_mail != "2":
                    print("Please select a valid option")
                    to_mail = input('''[1] Mail yourself this transaction 
    [2] Quit
    Please select anyone of the above options :  ''')

