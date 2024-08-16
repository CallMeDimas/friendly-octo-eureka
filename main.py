from anticaptchaofficial.funcaptchaproxyless import *
import requests
import random
from datetime import datetime, timezone
from modules.Username import GenerateUsername
import secrets
import string
import base64

def SolveCaptcha(unifiedCaptchaId, dataExchangeBlob):
    solver = funcaptchaProxyless()
    solver.set_verbose(1)
    solver.set_key('key')
    solver.set_website_url('https://www.roblox.com')
    solver.set_website_key('476068BF-9607-4799-B53D-966BE98E2B81')
    solver.set_js_api_domain('roblox-api.arkoselabs.com')
    data_blob = f"{{'blob':'{dataExchangeBlob}'}}"
    solver.set_data_blob(data_blob)
    solver.set_soft_id(0)

    token = solver.solve_and_return_solution()
    if token != 0:
        print('result token: '+token)
    else:
        print('task finished with error '+solver.error_code)

def CreateSession():
    session = requests.Session()
    session.headers.update({
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9',
        'cache-control': 'no-cache',
        'origin': 'https://www.roblox.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.roblox.com/',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    })
    return session

def CreateCsrf(session):
    session.headers.update({'authority': 'www.roblox.com'})
    response = session.get('https://www.roblox.com/')
    csrf_token = response.text.split('"csrf-token" data-token="')[1].split('"')[0]
    if not csrf_token:
        print('Cant Find CSRF_Token.')
    
    session.headers.update({'x-csrf-token': csrf_token})

def FindCookies(session):
    response = session.get('https://www.roblox.com/timg/rbx')
    session.cookies.update({"RBXcb": "RBXViralAcquisition=true&RBXSource=true&GoogleAnalytics=true"})
    params = {
        'name': 'ResourcePerformance_Loaded_funcaptcha_Computer',
        'value': '2',
    }

    response = session.post('https://www.roblox.com/game/report-stats', params=params)

def GenerateBirthday():
    birthdate = (
        datetime(
            random.randint(1990, 2006),
            random.randint(1, 12),
            random.randint(1, 28),
            21,
            tzinfo=timezone.utc,
        )
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    return birthdate

def GeneratePasswd(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def VerifyUsername(session):
    session.headers.update({'authority': 'auth.roblox.com'})
    session.headers.update({'accept': 'application/json, text/plain, */*'})

    birthday = GenerateBirthday()
    nickname = GenerateUsername()

    response = session.get(
        f"https://auth.roblox.com/v1/validators/username?Username={nickname}&Birthday={birthday}",
    )

    return nickname, birthday

def GenerateNonce(session):
    session.headers.update({'authority': 'apis.roblox.com'})
    response = session.get('https://apis.roblox.com/hba-service/v1/getServerNonce')
    serverNonce = response.text.split('"')[1]
    return serverNonce

def GenerateRegister(username, birthday, session, nonce):
    account_passwd = GeneratePasswd()

    json_data = {
        "username": username,
        "password": account_passwd,
        "birthday": birthday,
        "gender": 2,
        "isTosAgreementBoxChecked": True,
        "agreementIds": [
            "adf95b84-cd26-4a2e-9960-68183ebd6393",
            "91b2d276-92ca-485f-b50d-c3952804cfd6",
        ],
        "secureAuthenticationIntent": {
            "clientPublicKey": "roblox sucks",
            "clientEpochTimestamp": str(time.time()).split(".")[0],
            "serverNonce": nonce,
            "saiSignature": "lol",
        },
    }

    session.headers.update({'authority': 'auth.roblox.com'})

    response = session.post('https://auth.roblox.com/v2/signup', json=json_data)

    if "Token Validation Failed" in response.text:
        session.headers.update({'x-csrf-token': response.headers['x-csrf-token']})
        response = session.post('https://auth.roblox.com/v2/signup', json=json_data)

    elif response.status_code == 429:
        print('The IP is Rate Limited.')

    captcha_response = json.loads(base64.b64decode(response.headers["rblx-challenge-metadata"].encode()).decode())
    unifiedCaptchaId = captcha_response["unifiedCaptchaId"]
    dataExchangeBlob = captcha_response["dataExchangeBlob"]
    genericChallengeId = captcha_response["sharedParameters"]["genericChallengeId"]

    SolveCaptcha(unifiedCaptchaId, dataExchangeBlob)

def main():
    session = CreateSession()
    csrf_token = CreateCsrf(session)
    cookies = FindCookies(session)
    username, birthday = VerifyUsername(session)
    nonce = GenerateNonce(session)
    register = GenerateRegister(username, birthday, session, nonce)

main()
