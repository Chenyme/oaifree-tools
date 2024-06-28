import json
import requests


def get_accesstoken(refresh_token):
    url = "https://token.oaifree.com/api/auth/refresh"
    data = {
        "refresh_token": refresh_token
    }
    response = requests.post(url, data=data)
    response_text = response.text
    data_dict = json.loads(response_text)
    access_token = data_dict.get("access_token", None)
    return access_token


def get_sharetoken(name, access_token, site_limit, expires_in, gpt35_limit, gpt4_limit, show_conversations):
    data = {
        'unique_name': name,
        'access_token': access_token,
        'site_limit': site_limit,
        'expires_in': expires_in,
        'gpt35_limit': gpt35_limit,
        'gpt4_limit': gpt4_limit,
        'show_conversations': show_conversations,
        'show_userinfo': 'false',
        'reset_limit': 'false'
    }
    response = requests.post('https://chat.oaifree.com/token/register',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=data)
    response_text = response.text
    data_dict = json.loads(response_text)
    token_key = data_dict.get("token_key", None)
    return name, token_key


def get_login_url(yourdomain, sharetoken):
    url = f'https://{yourdomain}/api/auth/oauth_token'
    headers = {
        'Origin': f'https://{yourdomain}',
        'Content-Type': 'application/json'
    }
    data = {
        'share_token': sharetoken
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json().get('login_url')


def df_to_json1(df):
    json_data = df.to_dict('records')
    json_data = {str(record['用户组']): {
        'account_type': record['订阅类型'],
        'account': record['账户邮箱'],
        'access_token': record['AC_Token'],
        'refresh_token': record['RF_Token']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json2(df):
    json_data = df.to_dict('records')
    json_data = {str(record['username']): {
        'password': record['password'],
        'token': record['token'],
        'group': record['group'],
        'type': record['type'],
        'site_limit': record['site_limit'],
        'expires_in': record['expires_in'],
        'gpt35_limit': record['gpt35_limit'],
        'gpt4_limit': record['gpt4_limit'],
        'show_conversations': record['show_conversations']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json3(df):
    json_data = df.to_dict('records')
    json_data = {str(record['invite_token']): record['group'] for record in json_data}
    return json_data, json.dumps(json_data, indent=2)

