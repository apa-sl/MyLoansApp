from decimal import Decimal, ROUND_DOWN
import mysql.connector
from datetime import datetime

loan = {}
loan["name"] = "test"
loan["vendor_id"] = 1
loan["installment_amount"] = Decimal(90)
loan["start_date"] = datetime.strptime("2022-12-10", '%Y-%m-%d')
loan["installments_count"] = int(float(10))
loan["due_day"] = int(float(3))
loan["last_installment_diff"] = False

db = mysql.connector.connect(
    host="127.0.0.1",
    user="remote-myloansapp",
    password="GWgAHuh1hyhr24OeVnjx",
    database="myloansapp"
)
# initialize a cursor that is always catching all rows from the query and as dicts (not as tuples)
cursor = db.cursor(buffered=True, dictionary=True)

# calculate loan total amount
if loan["last_installment_diff"] == True:
    loan["amount_total"] = loan["installment_amount"] * (loan["installments_count"] - 1) + loan["last_installment_amount"]

else:
    loan["amount_total"] = loan["installment_amount"] * loan["installments_count"]

print(loan)
try:
            # add loan to the loans table & get id of the newly created loan
    query = ("INSERT INTO loans (name, user_id, vendor_id, start_date, agreement_id, due_day, loan_amount_total, loan_amount_outstanding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    data = (loan["name"], 1, loan["vendor_id"], loan["start_date"], loan["start_date"], loan["due_day"], loan["amount_total"], loan["amount_total"])
            # TODO: pass real user id from the session
    cursor.execute(query, data)
    loan["id"] = cursor.lastrowid
    print(loan["id"])
            #loan["id"] = cursor.fetchone()

    for i in loan["installments_count"]:
        print(i)
        #query = "INSERT INTO installments (loan_id, amount) VALUES (%s, %s)"
        #data = (loan["id"], loan["installment_std_amount"])
        #cursor.execute(query, data)

    # commit changes in the database
    db.commit()

except:
            # rollback in case of error
    db.rollback()
