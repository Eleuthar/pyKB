# 'INC000036441199\t10/25/2024 10:35:30 PM\n'
# to 11/24/2024 10:14:43 PM
from datetime import datetime

with open('reptime.txt') as rp:
    for q in rp.readlines():
        tt = q.split('\t')[0]
        dt = q.split('\t')[1].split()[0].rstrip()
        pm = ' '.join(q.split()[2:]).rstrip()
        tm = datetime.strptime(pm, "%I:%M:%S %p").strftime("%H:%M:%S")
        rpd[tt] = dt+" "+tm