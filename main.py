import requests
import json

def get_token():
    with open('creds.json') as json_creds:
        creds = json.load(json_creds)

    url = "https://traction.tools\Token"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'password', 
            'userName': creds.get('traction_user'), 
            'password': creds.get('traction_pass')
            }
    r = requests.post(url, data=data, headers=headers)
    json_data = r.json()
    token = json_data.get('access_token')
    return token

def get_personal_todos(token):
    url = "https://traction.tools/api/v1/todo/users/mine"
    bearer_token = f'Bearer {token}'
    headers = {'Accept': 'application/json',
               'Authorization':bearer_token
               }
    r = requests.get(url, headers=headers).json()
    todos = [(todo['Origin'], todo['Name']) for todo in r ]
    return todos


bearer_token = get_token()
todos = get_personal_todos(bearer_token)
print(todos)
