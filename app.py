import requests
import mysql.connector
from datetime import datetime
import time
import sys
import threading as th
import tkinter
import multiprocessing as mp
from multiprocessing import Pool


def read_token():
    with open("token.txt", "r") as f:
        token = f.read()
        return token.strip()


def slot_check(cid, cursor, headers):
    endpoint = f"https://cvp1.moph.go.th/api/ImmunizationTarget?cid={cid}"
    r = requests.get(endpoint, headers=headers, verify=False)
    data = r.json()
    try:
        data = data['result']['confirm_appointment_slot'][0]
        hoscode = data['hospital_code']
        hosname = data['hospital_name']
        slot_id = data['hospital_appointment_slot_id']
        slot_date = data['appointment_date']
        slot_time = data['appointment_time']
        app_type = data['appointment_type']
        dose = data['dose']

        sql_update = f""" update slot_result t set  t.hoscode = '{hoscode}',t.hosname='{hosname}' 
                        ,t.slot_id = "{slot_id}",t.slot_date = '{slot_date}',t.slot_time = '{slot_time}'
                        ,t.dose = '{dose}',t.plk_result_date = NOW() ,t.book_type = '{book_type}'  where t.cid = '{cid}'
                    """

        cursor.execute(sql_update)
        return ('ok', cid, data)


    except Exception as err:
        return (cid, "ไม่พบ", err)


def plk_list_get_slot(date, cursor, headers):
    sql = f"SELECT cid FROM slot_result where date(plk_date)='{date}' and slot_id is null"
    print(f"Thread : {date}", sql)
    cursor.execute(sql)

    my_result = cursor.fetchall()

    i = 0
    for row in my_result:
        i += 1
        _cid = row[0]
        print(i, date, slot_check(_cid, cursor, headers))
        time.sleep(0.5)


if __name__ == '__main__':
    requests.urllib3.disable_warnings()
    token = read_token()
    headers = {"Authorization": f"Bearer {token}"}

    con = mysql.connector.connect(
        host="plkprom.plkhealth.go.th",
        port=3366,
        user="sa",
        password="qazwsxedcr112233",
        database="plkprom"
    )
    con.autocommit = True
    cursor = con.cursor(dictionary=False)

    jobs = []
    jobs.append(th.Thread(target=plk_list_get_slot('2021-05-17', cursor, headers), daemon=True))
    jobs.append(th.Thread(target=plk_list_get_slot('2021-05-16', cursor, headers), daemon=True))

    for j in jobs:
        j.start()

        # Ensure all of the threads have finished
    for j in jobs:
        j.join()
