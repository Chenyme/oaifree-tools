import streamlit as st
import requests
import json
import toml
import pandas as pd
import os

current_path = os.path.abspath('.')
with open(current_path + '/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    acoounts = json.load(file)
with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    websetting = toml.load(file)


def authenticate(username, password):
    account = config.get(username)
    return account and account['password'] == password


def login(username, password):
    if authenticate(username, password):
        account = config[username]
        login_result = 1
        return login_result, account['token'], account['group']
    else:
        login_result = 0
        return login_result, None, None


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


def get_sharetoken(name, accesstoken):
    data = {
        'unique_name': name,
        'access_token': accesstoken,
        'site_limit': '',
        'expires_in': '0',
        'gpt35_limit': '-1',
        'gpt4_limit': '-1',
        'show_conversations': 'false',
        'show_userinfo': 'false',
        'reset_limit': 'false'
    }
    response = requests.post('https://chat.oaifree.com/token/register', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=data)
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
    json_data = {str(record['groups']): {
        'Account': record['Account'],
        'access_token': record['access_token'],
        'refresh_token': record['refresh_token']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


def df_to_json2(df):
    json_data = df.to_dict('records')
    json_data = {str(record['username']): {
        'password': record['password'],
        'token': record['token'],
        'group': record['group']
    } for record in json_data}
    return json.dumps(json_data, indent=2)


st.set_page_config(
    page_title="OpenAI,Not CloseAI",
    page_icon="🔓"
)

with st.popover("links", disabled=False, use_container_width=False):
    st.markdown("[Linux.do](https://linux.do/)")
    st.markdown("[ ️zhile.io](https://zhile.io/)")
    st.markdown("[ ️Chenyme's Github](https://github.com/Chenyme)")

st.write("")
st.markdown("<div style='text-align:center;'><h1 style='text-align:center;'>OpenAI , Not  CloseAI</h1></div>",
            unsafe_allow_html=True)
st.write("")
st.write("")

col1, col2, col3 = st.columns([0.27, 0.46, 0.27])
with col2:
    account = st.text_input("**Account**")
    password = st.text_input("**Password**", type="password")
    st.write("---")
    if st.button("**LOGIN**", use_container_width=True):
        login_result, token_result, group_result = login(account, password)
        if login_result:
            yourdomain = websetting["web"]["yourdomain"]
            url = get_login_url(yourdomain, token_result)
            st.toast('Success!', icon='🎉')
        else:
            st.toast('Error!', icon='😞')
    try:
        st.link_button("**Click To Verify**", url, use_container_width=True, type="primary")
    except:
        a = 1

    popover = st.popover("**More Options**", use_container_width=True)
    choose = popover.selectbox("Choose your identity", ["Click me", "User", "Admin"], index=0)
    if choose == "Admin":
        key = popover.text_input("Super key")
    st.write("")
    st.write("")
    st.write("")
    st.markdown("<div style='text-align:center;'><p><strong>Powered by @Neo, </strong> <strong>Created by @Chenyme</strong></p></div>", unsafe_allow_html=True)

    if choose == "User":
        st.write("---")
        with st.expander("**账号修复**", expanded=False):
            st.write("")
            st.write("###### 有问题请去admin修改相关token")
            st.write("")
            account2 = st.text_input("账号")
            password2 = st.text_input("密码", type="password")
            login_result, token_result, group_result = login(account2, password2)
            st.write("")
            if st.button("账户修复", use_container_width=True, type="primary"):
                if account2 != "" and password2 != "":
                    if login_result == 1:
                        re_tk = acoounts[group_result]["refresh_token"]
                        ac_tk = get_accesstoken(re_tk)
                        if ac_tk is None:
                            st.toast("刷新失败！", icon='😞')
                        else:
                            nam, sha = get_sharetoken(account2, ac_tk)
                            if sha == token_result:
                                acoounts[group_result]["access_token"] = ac_tk
                                acoounts_json = json.dumps(acoounts, indent=2)
                                json_filename = 'accounts.json'
                                with open(json_filename, 'w', encoding='utf-8') as json_file:
                                    json_file.write(acoounts_json)
                                st.toast("修复成功！", icon='🎉')
                            else:
                                st.toast("修复失败，请联系管理员！", icon='🎉')
                    elif login_result == 0:
                        st.toast('账户密码错误!', icon='😞')
                else:
                    st.toast('请输入账户密码!', icon='😞')

if choose == "Admin" and key == websetting["web"]["superkey"]:
    st.write("---")
    st.write("##### 若为首次登入，请立即修改superkey！！！")
    with st.expander("**网站管理**", expanded=True):
        domain = st.text_input("修改域名", value=websetting["web"]["yourdomain"])
        super_key = st.text_input("**修改superkey**", value=websetting["web"]["superkey"])
        if st.button("保存更改", use_container_width=True, type="primary"):
            websetting["web"]["yourdomain"] = domain
            websetting["web"]["superkey"] = super_key
            with open("setting.toml", "w") as f:
                toml.dump(websetting, f)
            st.toast("保存成功！", icon='🎉')

    with st.expander("**账户管理**", expanded=False):
        st.write('')
        rows = [[groups, datas['Account'], datas['access_token'], datas['refresh_token']]  # 将字典转换为列表的列表，以便于pandas处理
                for groups, datas in acoounts.items()]
        st.write("###### Group一旦输入确定，请勿随意修改")
        st.write('')
        df1 = pd.DataFrame(rows, columns=['groups', 'Account', 'access_token', 'refresh_token'])
        edited_df1 = st.data_editor(df1, hide_index=True, use_container_width=True, num_rows="dynamic")
        st.write('')
        if st.button("保存账户修改", use_container_width=True, type="primary"):
            json_data1 = df_to_json1(edited_df1)
            json_filename = 'accounts.json'
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data1)
            st.toast('Success!', icon='🎉')

    with st.expander("**刷新access_token**", expanded=False):
        ac_group = st.selectbox("要刷新的组别（账号）", acoounts.keys())
        if st.button("刷新", use_container_width=True, type="primary"):
            re_tk = acoounts[ac_group]["refresh_token"]
            ac_tk = get_accesstoken(re_tk)
            if ac_tk is None:
                st.toast("刷新失败！", icon='😞')
            else:
                acoounts[ac_group]["access_token"] = ac_tk
                acoounts_json = json.dumps(acoounts, indent=2)
                json_filename = 'accounts.json'
                with open(json_filename, 'w', encoding='utf-8') as json_file:
                    json_file.write(acoounts_json)
                st.toast("刷新成功！", icon='🎉')
                st.toast(ac_tk, icon='🎉')

    with st.expander("**用户注册**", expanded=False):
        st.write('')
        new_acc = st.text_input("用户名")
        new_pass = st.text_input("密码")
        new_group = st.selectbox("组别", acoounts.keys())
        st.write('')
        if st.button("SIGN UP", use_container_width=True, type="primary"):
            if new_acc == "" or new_pass == "":
                st.toast('请输入账户密码!', icon='😞')
            if new_acc in config:
                st.toast('用户名已存在!', icon='😞')
            else:
                group_data = acoounts[new_group]
                acc = group_data['access_token']
                new_name, new_token_key = get_sharetoken(new_acc, acc)
                json_data = {
                    new_name: {
                        'password': new_pass,
                        'token': new_token_key,
                        'group': new_group
                    }
                }
                config.update(json_data)
                config_json = json.dumps(config, indent=2)
                json_filename = 'config.json'
                with open(json_filename, 'w', encoding='utf-8') as json_file:
                    json_file.write(config_json)
                st.toast('Success!', icon='🎉')

    with st.expander("**用户管理**", expanded=False):
        st.write('')
        rows = [[user, account['password'], account['token'], account['group']]  # 将字典转换为列表的列表，以便于pandas处理
                for user, account in config.items()]
        df2 = pd.DataFrame(rows, columns=['username', 'password', 'token', 'group'])
        edited_df2 = st.data_editor(df2, hide_index=True, use_container_width=True, disabled=["username", "token", "group"], num_rows="dynamic")
        st.write('')
        if st.button("保存用户修改", use_container_width=True, type="primary", help="出于安全性考虑，只允许删除账户和修改账户密码。"):
            json_data2 = df_to_json2(edited_df2)
            json_filename = 'config.json'
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data2)
            st.toast('Success!', icon='🎉')