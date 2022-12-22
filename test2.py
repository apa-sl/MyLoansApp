from decimal import Decimal, ROUND_DOWN
import mysql.connector
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

print(date.today() + relativedelta(months=+1))
print(datetime.strptime("2022-12-10", "%d"))

db = mysql.connector.connect(
    host="127.0.0.1",
    user="remote-myloansapp",
    password="GWgAHuh1hyhr24OeVnjx",
    database="myloansapp"
)
# initialize a cursor that is always catching all rows from the query and as dicts (not as tuples)
cursor = db.cursor(buffered=True, dictionary=True)

loan={}
loan["vendor_name"] = 'Allegro Pay'
query = "SELECT id FROM vendors WHERE name = %s"
data = [(loan["vendor_name"])]
cursor.execute(query, data)
result = cursor.fetchone()
loan["vendor_id"] = result["id"] 
print(type(loan["vendor_id"]))