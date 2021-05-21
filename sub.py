import requests
import mysql.connector
from datetime import datetime
import time
import sys
import os
import configparser
import threading as th
import tkinter
import multiprocessing as mp
from multiprocessing import Pool

token_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.txt')


def read_token():
    with open(token_file, "r") as f:
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
        book_type = data['appointment_type']
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
    sql = f"SELECT cid FROM slot_result where date(plk_date)='{date}'"
    print(f"Thread : {date}", sql)
    cursor.execute(sql)

    my_result = cursor.fetchall()

    i = 0
    for row in my_result:
        i += 1
        _cid = row[0]
        print(i, date, slot_check(_cid, cursor, headers))
        time.sleep(0.2)


if __name__ == '__main__':
    conf_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')
    config = configparser.ConfigParser()
    config.read(conf_file, encoding='utf8')

    requests.urllib3.disable_warnings()
    token = read_token()
    headers = {"Authorization": f"Bearer {token}"}

    con = mysql.connector.connect(
        host=config['DB']['HOST'],
        port=config['DB']['PORT'],
        user=config['DB']['USER'],
        password=config['DB']['PASS'],
        database=config['DB']['DATABASE']
    )
    con.autocommit = True
    cursor = con.cursor(dictionary=False)
    arg = sys.argv
    _date = arg[1]
    plk_list_get_slot(_date, cursor, headers)
