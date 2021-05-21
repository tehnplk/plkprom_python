import requests
import os

token_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.txt')


def read_token():
    with open(token_file, "r") as f:
        token = f.read()
        return token.strip()


def cid_check(cid, headers):
    endpoint = f"https://cvp1.moph.go.th/api/ImmunizationTarget?cid={cid}"
    r = requests.get(endpoint, headers=headers, verify=False)
    data = r.json()
    return data


if __name__ == '__main__':
    requests.urllib3.disable_warnings()
    token = read_token()
    headers = {"Authorization": f"Bearer {token}"}
    cid = '3600100837441'
    data = cid_check(cid, headers)
    print(data)
