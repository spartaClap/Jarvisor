from datetime import datetime as dt
import datetime

print(dt.today().strftime("%Y-%m-%d"))


f_day = '2023-01-30'
format = '%Y-%m-%d'
dt = datetime.datetime.strptime(f_day, format).date()
print(dt)
print((dt-dt.today()).days)