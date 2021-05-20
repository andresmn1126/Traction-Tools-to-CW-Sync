import requests
import json
import base64
from helper import shorten_name, turn_to_lower, merge_list_of_dicts

with open('creds.json') as json_creds:
    creds = json.load(json_creds)


## CW related auth info
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
               'Authorization': bearer_token
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
        url = f"https://traction.tools/api/v1/todo/user/{user.get('ttid')}"
        r = requests.get(url, headers=headers).json()
        todos = [{'name': todo['Name'], 'due': todo['DueDate']} for todo in r if 'CW -' in todo['Name'][:3] and todo['Complete'] == False]
        user['todos'] = todos
        all_todos.append(user)
    return all_todos        

def get_cw_members():
    endpoint = "/system/members"
    params = {"pageSize": 1000,
              "field": "id,identifier"
             }
    r = requests.get(cwurl + endpoint, params=params, headers=cwheaders).json()
    cw_members = [{"name": turn_to_lower(member['identifier']), "cwid": member['id']} for member in r]
    return cw_members

def get_cw_active_activities(id):
    endpoint = "/sales/activities"
    params = {"fields": "name",
              "conditions": f"status/name='Open' AND assignTo/id={id}",
              "pageSize": 1000,
             }
    r = requests.get(cwurl + endpoint, headers=cwheaders, params=params).json()
    return [activity['name'] for activity in r]

def post_cw_activities(todos):
    endpoint = "/sales/activities"
    for user in todos:
        activities = get_cw_active_activities(user['cwid'])
        for todo in user['todos']:
            if todo['name'] not in activities:
                data = {"company": {"id": 2},
                        "name": todo['name'],
                        "assignTo": {"id": user['cwid']},
                        "notes": f"Marked as due on {todo['due']}"
                       }
                r = requests.post(cwurl + endpoint, headers=cwheaders, json=data)
                print(r.status_code)


if __name__ == "__main__":
    token = get_token()
    cw_ids = get_cw_members()
    tt_ids = get_tt_userids(token)
    combined_ids = merge_list_of_dicts(tt_ids, cw_ids)
    todos = get_tt_todos(token, combined_ids)
    post_cw_activities(todos)