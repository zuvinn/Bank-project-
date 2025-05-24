'''CREATE TABLE Customers (
    Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Date_Of_Birth DATE,
    Address VARCHAR(255),
    Phone_Number VARCHAR(20),
    Email VARCHAR(100),
    password varchar(10) NOT NULL
);
#dhakshin edit

CREATE TABLE Accounts (
    Account_ID INT AUTO_INCREMENT PRIMARY KEY,
    Customer_ID INT,
    Account_Type ENUM('Current', 'Savings') NOT NULL,
    Balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    Opened_date timestamp DEFAULT CURRENT_timestamp,
    FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID)
);


CREATE TABLE Transactions (
    Transaction_ID INT AUTO_INCREMENT PRIMARY KEY,
    Account_ID INT,
    Transaction_Type ENUM('Deposit', 'Withdrawal', 'Transfer') NOT NULL,
    Amount DECIMAL(15, 2) NOT NULL,
    Transaction_Date TIMEstamp DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Account_ID) REFERENCES Accounts(Account_ID)
);


CREATE TABLE Transfers (
    Transfer_ID INT AUTO_INCREMENT PRIMARY KEY,
    From_Account_ID INT(11) NOT NULL,
    To_Account_ID INT(11) NOT NULL,
    Amount DECIMAL(15, 2) NOT NULL,
    Transfer_Date TIMEstamp DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (From_Account_ID) REFERENCES Accounts(Account_ID),
    FOREIGN KEY (To_Account_ID) REFERENCES Accounts(Account_ID)
);
 '''
import mysql.connector as ms
obj = ms.connect(user='root', password ='vinu', host='localhost',database='bank')
cur=obj.cursor()
def transfer_amount(ids):
    while True:
        cur.execute('select to_account_id from transfers where from_account_id=%s and transfer_type="transfer" ',(ids,))
        frequent=cur.fetchall()
        print(frequent)
        freq_acc={}
        cur.execute('select from_account_id,count(*) from transfers where from_account_id=%s',(ids,))
        r=cur.fetchall()
        if r[0][1]>=3:
            n=3
        elif r[0][1]==2:
            n=2
        elif r[0][1]==1:
            n=1
        else:
            n=0 
        for i in frequent:
            v=i[0]
            if v not in freq_acc:
                for f in frequent:
                    count=0
                    if f[0]==v:
                        count+=1
                freq_acc[v]=count
                print(freq_acc)
        h=max(freq_acc,key=freq_acc.get)
        cur.execute('select account_id,first_name from accounts ,customers where account_id=%s',(h,))
        q=cur.fetchall()
        print('Account id:',q[0][0],'Name:',q[0][1])
        del freq_acc[h]
        to_acc=int(input('Enter the account id of the account you want to transfer:'))
        amt=float(input('Enter the amount you want to transfer:'))
        cur.execute('select 1 from accounts where account_id=%s',(to_acc,))
        acc=cur.fetchone()
        if acc==None:
            print('***There is no such account_id***')
        else:
            break
    cur.execute('select balance from accounts where account_id=%s',(ids,))
    balance=cur.fetchone()
    if balance[0]>=amt:
        if amt<200000:
            print('You can transfer through')
            print('\t\t1.Neft')
            print('\t\t2.IMPS')
            ch=int(input('Which of the above you prefer(1/2):'))
            if ch==1:
                print('Your transfer would be done within 2 hours:')
                cur.execute('update accounts set balance=balance-%s where account_id=%s',(amt,ids))
                cur.execute('update accounts set balance=balance+%s where account_id=%s',(amt,to_acc))
                cur.execute('insert into transfers(from_account_id,to_account_id,amount,transfer_type) values (%s,%s,%s,"transfer")',(ids,to_acc,amt))
                obj.commit()
                print('Transaction has been done successfully')
            elif ch==2:
                if amt<=1000:
                    charge=1
                elif amt<=10:
                    charge=0.25
                elif amt<=10000:
                    charge=7
                else:
                    charge=15
                print('You will be charged by Rs.',charge,'on your tranfer of Rs.',amt)
                print('On total amount withdrawn from your account is Rs.',charge+amt)
                cur.execute('update accounts set balance=balance+%s where account_id=%s',(amt,to_acc))
                cur.execute('update accounts set balance=balance-%s where account_id=%s',(amt+charge,ids))
                cur.execute('insert into transfers(from_account_id,to_account_id,amount,transfer_type) values (%s,%s,%s,"transfer")',(ids,to_acc,amt))
                obj.commit()
                print('Transaction has been done successfully')
            else:
                print('Please enter a valid choice')
        elif  amt>=200000:
            cur.execute('update accounts set balance=balance-%s where account_id=%s',(amt,ids))
            cur.execute('update accounts set balance=balance+%s where account_id=%s',(amt,to_acc))
            cur.execute('insert into transfers(from_account_id,to_account_id,amount,transfer_type) values (%s,%s,%s,"transfer")',(ids,to_acc,amt))
            obj.commit()
            print('Transaction has been done successfully')
        else:
            print('Please enter a valid choice')
    else:
            print('Insufficient balance')


def deposit_amount(ids):
    amt=float(input('Enter the amount you want to deposit:'))
    cur.execute('update accounts set balance=balance+%s where account_id=%s',(amt,ids))
    cur.execute('insert into transfers(to_account_id,amount,transfer_type) values (%s,%s,"deposit")',(ids,amt))
    print('Rs.',amt,'has been deposited')
    obj.commit() 


def withdraw_amount(ids):
    amt=float(input('Enter the amount you want to withdraw:'))
    cur.execute('select balance from accounts where account_id=%s',(ids,))
    balance=cur.fetchone()
    if balance[0]>=amt:
        cur.execute('update accounts set balance=balance-%s where account_id=%s',(amt,ids))
        cur.execute('insert into transfers(from_account_id,amount,transfer_type) values (%s,%s,"withdrawal")',(ids,amt))
        print('Rs.',amt,'has been withdrawn')
        obj.commit()
    else:
        print('Insufficient balance')


def view_bankbalance(ids):
    cur.execute('select balance from accounts where account_id=%s',(ids,))
    balance=cur.fetchone()
    print('Your current balance is Rs.',balance[0])
    obj.commit()

def history(ids):
    cur.execute('select transfer_id,from_account_id,to_account_id,amount,transfer_date,transfer_type from transfers where from_account_id=%s or to_account_id=%s',(ids,ids))
    data=cur.fetchall()
    from tabulate import tabulate
    table=tabulate(data,headers=[' transfer_id ' ,' from_account_id ',' to_account_id ',' amount ',' transfer_data ',' transfer_type '],tablefmt='grid',stralign='center',colalign='center')
    print(table)
    

    
def singleuser(ids,c_id):
    while True:
        print('Account opened')
        print('1.Transfer amount')
        print('2.Deposit amount')
        print('3.Withdraw amount')
        print('4.View bank balance')
        print('5.Create new account')
        print('6.View account statement')
        print('7.Log out')
        choice=int(input('Enter your choice:'))
        if choice==1:
            transfer_amount(ids)
        elif choice==2:
            deposit_amount(ids)
        elif choice==3:
            withdraw_amount(ids)
        elif choice==4:
            view_bankbalance(ids)
        elif choice==5:
            create_account(c_id)
        elif choice==6:
            history(ids)
        elif choice==7:
            print('Logged out')
            front_page()
            break
        else:
            print('Please enter a valid choice')

            
def create_account(c_id):
    print('To create a new account fill in the following details')
    while True:
        type=input('Do you want to create savings account(Y/N):')
        if type in ['y','Y']:
            type='savings'
            break
        elif type in ['n','N']:
            type=input('Do you want to create a current account(Y/N):')
            if type in ['n','N']:
                print('You can either create savings or current account') 
            elif type in ['y','y']:
                type='current'
                break
            else:
                print('Please enter a valid choice') 
        else:
            print('Plesae enter a valid choice') 
    while True:
        initial_deposit=float(input('Enter the amount you want to deposit(minimum Rs.500):'))
        if initial_deposit<500:
            print('Minimum deposit is Rs.500')
        else:
            break
    cur.execute('insert into accounts(customer_id,account_type,balance)values(%s,%s,%s)',(c_id,type,initial_deposit))
    print('Account created successfully')
    obj.commit()
    


def sign_up():
    print('To create a new account fill in the following details')
    while True:
        firstname=input('Enter your first name:')
        if firstname=='':
            pass
        else:
            break
    while True:
        lastname=input('Enter your last name:')
        if lastname=='':
            pass
        else:
            break
    from datetime import datetime
    while True:
        dob=input('Enter your Date of Birth(YYYY-MM-DD):')
        try:
            DOB=datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            print('***Date should be in the format (YYYY-MM-DD)***')
        else:
            break
    email=input('Enter your email id:')
    while True:
        no=input('Enter your mobile number:')
        if len(no)!=10 and not no.isdigit():
            print('****Invalid phone number****')
            print('Re-enter the number')
        else:
            break
    address=input('Enter your address:')
    while True:
             passwd=input('Enter a strong password(6-10 characters):')
             if len(passwd)>10 or len(passwd)<6:
                 print('***Password must be of 6-10 characters***')
             elif  10>=len(passwd) and len(passwd)>=6:
                check=input('Re-enter the password:')
                if passwd!=check:
                    print('***Password mismatched***')
                else:
                     value=(firstname,lastname,dob,email,no,address,passwd)
                     cur.execute('insert into customers (first_name,last_name,date_of_birth,email,phone_number,address,password) values(%s,%s,%s,%s,%s,%s,%s)',value)
                     print('Account created successfully')
                     obj.commit()
                     cur.execute('select customer_id from customers where first_name=%s and last_name=%s and phone_number=%s',(firstname,lastname,no))
                     c_id=cur.fetchone()
                     print('Your customer id is',c_id[0],'\n***Please keep it safe***')
                     break       


def login():
    c_id=int(input('Enter customer id:'))
    passwd=input('Enter password:')
    while True:
        cur.execute('select password from customers where customer_id=%s',(c_id,))
        original_pass=cur.fetchone()
        if passwd==original_pass[0]:
            cur.execute('select first_name from customers where customer_id=%s',(c_id,))
            fname=cur.fetchone()
            print('Welcome',fname[0],'!')
            while True:
                cur.execute('select account_id from accounts where customer_id=%s',(c_id,))
                ids=cur.fetchall()
                if len(ids)==1:
                    singleuser(ids[0][0],c_id)
                    break
                elif len(ids)==0:
                    print('There is no account with this customer id')
                    create=input('Do you want to create new account(Y/N):')
                    if create in ['n','N']:
                        print('You cannot do any further activity')
                        break
                    elif create in ['y','Y']:
                        create_account(c_id)
                        break
                    else:
                        print('***Enter a valid choice(Y/N)***')
                elif len(ids)>1:
                    print('Your accounts are:')
                    for acc in ids:
                        print(acc[0])
                    acc_id=int(input('Enter the account you want to open:'))
                    singleuser(acc_id,c_id)
                    break

        else:
            print('**Incorrect password**')
            passwd=input('Re-enter password:')
def front_page():
    while True:
        print('\t\t Welcome to vinu global bank ')
        print('\t\t\t 1.Sign up')
        print('\t\t\t 2.Login')
        print('\t\t\t 3.Exit')
        n=input('Enter your choice:')
        if n=='1':
            sign_up()
        elif n=='2':
            login()
        elif n=='3':
            obj.close()
            exit()
        else:
            print('*** Please enter a valid choice***')

    
front_page()

















        
