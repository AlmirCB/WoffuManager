import requests
import os
import re
from datetime import datetime
token = ""
user = ""
password=""
# user = ""
# password=""
store_doc_name = "data"
# presence_url = "https://gtd.woffu.com/api/users/414571/diaries/presence?fromDate=2021-08-01&pageIndex=0&pageSize=31&toDate=2021-08-31"
default_headers = {
        'Host': 'gtd.woffu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://gtd.woffu.com/',
#         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#         'Content-Length': '72',
#         'Origin': 'https://gtd.woffu.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'TE': 'Trailers',
    }

# UTILS
def get_auth_headers(token):
    """ 
    Adds token to default headers
    return: headers with token authentication
    """
    headers = default_headers
    headers['Authorization'] = f"Bearer {token}"
    return headers

def eval_response(resp):
    """
    Evaluates a request response
    return: response as a dict
    """

    return eval(resp.text.replace("null", "None").replace("false", "False").replace("true", "True"))



# CONNECTION AND TOKEN MANAGEMENT

def store_access_token(user, token):
    """
    Adds token to user in datafile, create new register if it does not exists or replace the existing one.
    """
    with open(f"./{store_doc_name}", "w+") as file:
        try:
            token_dict = eval(file.read())
        except:
            token_dict = {}

        token_dict[user] = token
        file.write(str(token_dict))

def find_stored_access_token(user):
    """
    Searchs token inside data file by user
    return: token or None if no token is found.
    """
    with open(f"./{store_doc_name}", "r") as file:
        token_dict = eval(file.read())
    res = token_dict[user] if user in token_dict else None
    return res

def get_access_token(user, password):
    """
    Sends post with user and password to woffu
    return: token
    """
    login_payload=f"grant_type=password&username={user.replace('@','%40')}&password={password}"

    login_url = "https://gtd.woffu.com/token"

    r = requests.post(login_url, headers=default_headers, data=login_payload)

    r_dict = eval(r.content)
    access_token = r_dict['access_token']
    return(access_token)

def connect(user, password):
    """
    Search user's stored token, if not exists post user/pass to Woffu to get token
    return: user's access token
    """
    res = find_stored_access_token(user)
    if not res:
        res = get_access_token(user, password)
        store_access_token(user, res)
    return res


# User management
def get_user_info(token):
    url = "https://gtd.woffu.com/api/users/"
    headers = get_auth_headers(token)
    r = requests.get(url, headers=headers)
    return eval_response(r)

def get_user_id(token):
    user_info = get_user_info(token)
    return(user_info["UserId"])

# Assistence management

def get_diary(token):
    user_id = get_user_id(token)
    init = datetime(2021, 5, 1)
    end = datetime(2021, 8, 31)
    init_str = init.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    headers = get_auth_headers(token)
    url = f"https://gtd.woffu.com/api/users/{user_id}/diaries/presence?fromDate={init_str}&toDate={end_str}"

    r = requests.get(url, headers=headers)
    return eval_response(r)


def get_hours(diary):
    
    total_computed = 0
    total_days = 0
    for day in diary["Diaries"]:
        # print(day)
        if not day['IsWeekend'] and not day['IsHoliday'] and not day['IsEvent'] and not day['IsDisabled']:
            # hours = []
            hour_pairs = []
            date = datetime.strptime(day['Date'], "%Y-%m-%dT%H:%M:%S.%f")
            total_day = 0
            if day['TrueBreaks']:
                # hours = re.split(' |•', day['TrueBreaks'])
                hour_pairs = [hour.split("•") for hour in day['TrueBreaks'].split(" ")]
                for pair in day['TrueBreaks'].split(" "):
                    hours = pair.split("•")
                    if len(hours) == 2:
                        total_day += int(hours[1].split(":")[0]) * 60 + int(hours[1].split(":")[1])
                        total_day -= int(hours[0].split(":")[0]) * 60 + int(hours[0].split(":")[1])

                    elif len(hours) == 1:
                        total_day += datetime.now().hour * 60 + datetime.now().minute
                        total_day -= int(hours[0].split(":")[0]) * 60 + int(hours[0].split(":")[1])
            if total_day > 0:
                total_days += 1
                total_computed += total_day
                total_hours = int(total_day/60 - (total_day/60) % 1)
                total_min = int(((total_day/60) % 1)*60)
                print(f"{date} - {total_hours}:{total_min}")
        

    total_computed_hours = int(total_computed/60 - (total_computed/60) % 1)
    total_computed_min = int(((total_computed/60) % 1)*60)
    print(total_computed)
    print(f"{total_computed_hours}:{total_computed_min}")
    print(total_days * 8)

token = connect(user, password)
diary = get_diary(token)
get_hours(diary)
# print(diary)
