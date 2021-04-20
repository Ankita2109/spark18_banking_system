import hashlib
import numpy as np
import re
from transaction import transaction


class loginManage:

    def input_values(self):
        self.tr = transaction()
        customer_data = np.load("customer_data.npy", allow_pickle=True).tolist()
        option = input('''[1] Login 
        [2] Register 
        [3] Login as Manager
        [4] Quit
        Please select anyone of the above options: ''')
        while option != "4":
            if option == "1":
                self.do_login(customer_data)
            elif option == "2":
                self.do_register(customer_data)
            elif option == "3":
                self.do_manager_login(customer_data)
            elif option == "4":
                print("Bye Bye!")
            else:
                print("Please enter a valid option")
            option = input('''[1] Login
        [2] Register
        [3] Login as Manager
        [4] Quit
        Please select anyone of the above options: ''')
        return customer_data

    def do_login(self,customer_data):

        login_id = input("Please enter your login id : ")
        login_pwd = input("please enter your password : ")
        if (login_id in customer_data) and (
                customer_data[login_id]["pwd"] == hashlib.sha256(
            login_pwd.encode("utf8")).hexdigest()):
            print("loggedIn")
            trans_hist = self.tr.load_transaction_history(login_id)
            self.tr.do_transaction(customer_data, login_id, trans_hist)
            self.tr.save_transaction_history(trans_hist, login_id)
        else:
            print("Invalid UserId or Password")


    def do_register(self,customer_data):
        login_id = input("Please enter your email id : ")
        login_pwd_0 = input("please enter your password : ")
        login_pwd_1 = input("confirm password : ")
        if login_pwd_0 == login_pwd_1:
            customer_data[login_id] = {
                "balance": 0.0,
                "pwd": hashlib.sha256(
                    login_pwd_0.encode("utf8")).hexdigest()
            }
            np.save("customer_data.npy", customer_data)
            print("You have been registered, current balance : ",
                  customer_data[login_id]["balance"])

        else:
            print("Passwords don't match")


    def do_manager_login(self,customer_data):

        manager_id = input("Please enter manager id: ")
        manager_pwd = input("Please enter manager password: ")

        if (manager_id == transaction.config["manager_id"]) and (
                hashlib.sha256(manager_pwd.encode("utf8")).hexdigest() ==
                hashlib.sha256(
                    transaction.config["manager_pwd"].encode("utf8")).hexdigest()):
            ch = "y"
            while(ch == "y" or ch == "Y"):
                print("\nList of customers in our database: ")
                key_index = []
                index = 0
                for email_id in customer_data:
                    if email_id != manager_id:
                        print(index, email_id)
                        key_index.append(email_id)
                        index += 1
                selection = input(
                    "\nplease select the indexes of customers you want to view transactions for, separated by spaces: ")
                selected_indices = np.unique(re.findall(r"\b\d+\b", selection))
                if len(selected_indices) :
                    found = False
                    for index in selected_indices:
                        if int(index) < len(key_index) and int(index) > -1:
                            print(index, key_index[int(index)])
                            found = True
                    if found :
                        print("you have selected the following valid indices : ")
                        for index in selected_indices:
                            if int(index) < len(key_index) and int(index) > -1:
                                print("view transactions for : ", key_index[int(index)])
                                self.tr.view_download_transaction(key_index[int(index)], manager_id)
                    else :
                        print("you have not selected any valid indices")
                else :
                    print("you have not selected any valid indices")
                ch = input("select again, 'y' for yes: " )
        else:
            print("Invalid Manager Password")


