import requests
import mysql.connector
from datetime import datetime
import time

PLK_HOS = ('10676', '11251', '11252', '11253', '11254', '11255', '11256', '11257', '11455', '11517', '14972')


def read_token():
    with open("token.txt", "r") as f:
        token = f.read()
        return token.strip()


def slot_check(cid):
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

        sql_update = f""" update slot_result t set  t.hoscode = '{hoscode}',t.hosname='{hosname}(โดย-{app_type})' 
                ,t.slot_id = "{slot_id}",t.slot_date = '{slot_date}',t.slot_time = '{slot_time}'
                ,t.dose = '{dose}',t.plk_result_date = NOW()  where t.cid = '{cid}'
            """
        if hoscode in PLK_HOS:
            mycursor.execute(sql_update)
            return ('ok', cid, data)
        else:
            return ('not plk', cid, data)


    except Exception as err:
        return (cid, "ไม่พบ", err)


if __name__ == '__main__':
    requests.urllib3.disable_warnings()
    token = read_token()
    headers = {"Authorization": f"Bearer {token}"}

    mydb = mysql.connector.connect(
        host="61.19.112.243",
        port=3366,
        user="sa",
        password="qazwsxedcr112233",
        database="plkprom"
    )
    mydb.autocommit = True

    mycursor = mydb.cursor(dictionary=False)

    sql = f"SELECT cid FROM slot_result where date(plk_date)='2021-05-18'"
    mycursor.execute(sql)

    myresult = mycursor.fetchall()

    i = 0
    for x in myresult:
        time.sleep(.5)
        i += 1
        print(i, slot_check(x[0]))
