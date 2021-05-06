import requests
import json
import base64
import datetime

from requests.api import head
from helper import shorten_name

with open('creds.json') as json_creds:
    creds = json.load(json_creds)


## CW realated auth info
    cwurl = creds.get('CW_URL')
    cwclient_id = creds.get('CW_CLIENTID')
    cwpubkey = creds.get('CW_PUBLICKEY')
    cwprivkey = creds.get('CW_PRIVATEKEY')
    cwcompany = creds.get('CW_COMPANYID')
    cwauth_string = f"{cwcompany}+{cwpubkey}:{cwprivkey}"
    cwencoded_bytes = base64.b64encode(cwauth_string.encode("utf-8"))
    cwencoded_str = str(cwencoded_bytes, "utf-8")
    cwheaders = {"Authorization": f"Basic {cwencoded_str}",
               "clientId": cwclient_id
                }
 

def get_token():
    url = "https://traction.tools\Token"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'password', 
            'userName': creds.get('TT_USER'), 
            'password': creds.get('TT_PASS')
            }
    r = requests.post(url, data=data, headers=headers)
    json_data = r.json()
    token = json_data.get('access_token')
    return token

def get_tt_userids(token):
    url = "https://traction.tools/api/v1/users/mineviewable"
    bearer_token = f'Bearer {token}'
    headers = {'Accept': 'application/json',
               'Authorization':bearer_token
               }
    r = requests.get(url, headers=headers).json()
    tt_userids = [{"name": shorten_name(user['Name']), "ttid": user['Id']} for user in r]
    return tt_userids

def get_tt_todos(token, tt_dict):
    bearer_token = f'Bearer {token}'
    headers = {'Accept': 'application/json',
               'Authorization': bearer_token
               }
    all_todos = []
    for user in tt_dict:
        if user['name'] == 'amartinez':
            url = f"https://traction.tools/api/v1/todo/user/{user.get('ttid')}"
            r = requests.get(url, headers=headers).json()
            todos = [todo['Name'] for todo in r if 'CW' in todo['Name'][:2]]
            user['todos'] = todos
            all_todos.append(user)
    return all_todos        

def get_cw_members():
    endpoint = "/system/members"
    params = {"pageSize": 1000,
              "field": "id,identifier"
             }
    r = requests.get(cwurl + endpoint, params=params, headers=cwheaders).json()
    cw_members = [{"name": member['identifier'], "cwid": member['id']} for member in r]
    return cw_members

def get_cw_active_activities():
    endpoint = "/sales/activities"
    params = {"fields": "name",
              "conditions": "status/name='Open' AND assignTo/name='Andres Martinez'",
              "pageSize": 1000,
              "page": 1
             }
    r = requests.get(cwurl + endpoint, headers=cwheaders, params=params).json()
   #return [a['name'] for a in r]
    return [activity['name'] for activity in r]

def post_cw_activities(activities, todos):
    '''
    data = {"company": {"id": 2},
            "name": "Python Test",
            "id" : 0,
            "assignTo": {"id": 401},
            "contact": {"id": 401}
           }
    '''
    for todo in todos:
        data = {"company": {"id": 2},
                "name": todo,
                "assignTo": {"id": 401}
               }
        r = requests.post(cwurl, headers=cwheaders, json=data)

'''
token = get_token()
todos = get_personal_todos(token)
activities = get_cw_active_activities()
post_cw_activities(activities, todos)
'''

token = get_token()
tt_ids = get_tt_userids(token)
todos = get_personal_todos(token, tt_ids)
print(todos)