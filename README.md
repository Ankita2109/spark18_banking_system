This is a banking system written in python 3.8
It supports the following features:
1. You can login as an existing customer or register as a new customer. Customer can make the following transactions:

	a. Deposit
	
	b. Withdraw
	
	c. Balance Enquiry
	
	Customer will recieve mails for each transaction other than balance enquiry.
2. You can login as a manager and mail yourself the transactions of individual or multiple customers; manager credentials are in the "config.json" file.
3. We have setup a test mailbox "spark18test@gmail.com", mailbox credentials are in the "config.json" file.  

To initialize the project :
1. create a new python or conda virtual environment.
2. Add the packages in the requirements.txt file using the following command:

		pip install -r requirements.txt
3. Run "app.py" file : 

		python app.py
