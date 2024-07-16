import math
import json
import requests


def check_sharetoken(share_token):
    url = f"https://chat.oaifree.com/token/info/{share_token}"
    response = requests.get(url, timeout=(5, 5))
    if response.status_code == 200:
        return True
    else:
        return False


def get_accesstoken(refresh_token):
    url = "https://token.oaifree.com/api/auth/refresh"
    data = {
        "refresh_token": refresh_token
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        status = True
        response_text = response.text
        data_dict = json.loads(response_text)
        access_token = data_dict.get("access_token", None)
    else:
        status = False
        access_token = None
    return status, access_token


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
    if response.status_code == 200:
        response_text = response.text
        data_dict = json.loads(response_text)
        token_key = data_dict.get("token_key", None)
        status = True
    else:
        status = False
        name = None
        token_key = None
    return status, name, token_key


def get_oaifree_login_url(yourdomain, sharetoken):
    url = f'https://{yourdomain}/api/auth/oauth_token'
    headers = {
        'Origin': f'https://{yourdomain}',
        'Content-Type': 'application/json'
    }
    data = {
        'share_token': sharetoken
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('login_url')
    else:
        return False


def get_fucladue_login_url(url, token, name):
    url = f'https://{url}/manage-api/auth/oauth_token'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'session_key': token,
        'unique_name': name
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('login_url')
    else:
        return False


def get_size(size_bytes):
    if size_bytes == 0:
        size = "0B"
    else:
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        size = f"{s} {size_name[i]}"
    return size


def df_to_json_account(df):
    json_data = df.to_dict('records')
    json_data = {str(record['用户组']): {
        'service_provider': record['服务商'],
        'account_type': record['订阅类型'],
        'account': record['账户邮箱'],
        'access_token': record['AC_Token'],
        'refresh_token': record['RF_Token']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json_oaifree(df):
    json_data = df.to_dict('records')
    json_data = {str(record['账户']): {
        'token': record['SA_Token'],
        'group': record['用户组'],
        'type': record['订阅类型'],
        'site_limit': record['限制网站'],
        'expires_in': record['过期秒数'],
        'gpt35_limit': record['GPT3.5限制'],
        'gpt4_limit': record['GPT4限制'],
        'show_conversations': record['会话无需隔离']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json_invite(df):
    json_data = df.to_dict('records')
    json_data = {str(record['Invite_Token']): {
        "openai-group": record['OpenAI_用户组'],
        "chatgpt": record['ChatGPT'],
        "anthropic-group": record['Anthropic_用户组'],
        "claude": record['Claude'],
        "note": record['备注'],
        "used": record['是否使用'],
        "site_limit": record['限制网站'],
        "expires_in": record['过期秒数'],
        "gpt35_limit": record['GPT3.5限制'],
        "gpt4_limit": record['GPT4限制'],
        "show_conversations": record['会话无需隔离'],
        "claude_limit": record['限制网站-claude'],
        "expires_in_claude": record['过期秒数-claude'],
        "show_conversations_claude": record['会话无需隔离-claude'],
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json4(df):
    json_data = df.to_dict('records')
    json_data = {str(record['userRF_Token']): {
        'group': record['用户组'],
        'site_limit': record['限制网站'],
        'expires_in': record['过期秒数'],
        'gpt35_limit': record['GPT3.5限制'],
        'gpt4_limit': record['GPT4限制'],
        'show_conversations': record['会话无需隔离'],
        'note': record['备注'],
        'used': record['是否使用']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json_domain(df):
    json_data = df.to_dict('records')
    json_data = {str(record['服务域名']): {
        'name': record['名称'],
        'speed': record['延迟'],
        'type': record['类型']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json_user_data(df):
    json_data = df.to_dict('records')
    json_data = {str(record['账户']): {
        'password': record['密码'],
        'uid': record['UID'],
        'allow_chatgpt': record['ChatGPT'],
        'allow_claude': record['Claude'],
        'note': record['备注']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json_fuclaude(df):
    json_data = df.to_dict('records')
    json_data = {str(record['账户']): {
        'token': record['SE_Token'],
        'group': record['用户组'],
        'type': record['订阅类型']
    } for record in json_data}
    return json.dumps(json_data, indent=2)