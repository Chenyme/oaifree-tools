import os
import json
import toml
import base64
import logging
import streamlit as st
import streamlit_antd_components as sac
from utils import get_accesstoken, get_sharetoken

current_path = os.path.abspath('.') + '/config/'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(current_path + "app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

with open(current_path + '/invite.json', 'r', encoding='utf-8') as file:
    invite_config = json.load(file)
with open(current_path + '/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    accounts = json.load(file)
with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    web_setting = toml.load(file)
with open(current_path + '/refresh.json', 'r', encoding='utf-8') as file:
    refresh_data = json.load(file)
with open("LOGO.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

version = "v1.1.5"


def authenticate(username, password):
    account = config.get(username)
    return account and account['password'] == password


def login(username, password):
    if username == web_setting['web']['super_user'] and password == web_setting['web']['super_key']:
        return 3, None, 'admin'
    elif username not in config:
        return 0, None, None
    elif authenticate(username, password):
        account = config[username]
        return 2, account['token'], account['group']
    else:
        return 1, None, None


st.set_page_config(layout="wide", page_title=web_setting["web"]["title"], page_icon="LOGO.png")

if web_setting["web"]["button_style"] == "Classic-black":
    st.markdown("""
        <style>
        .st-emotion-cache-keje6w.e1f1d6gn3 {
            float: right !important;
            text-align: right !important;
            display: inline-block;
        }
        .st-emotion-cache-1vt4y43 {
            background-color:  white !important;
            color: black !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
        }
        .eyeqlp52.st-emotion-cache-1pbsqtx.ex0cdmw0 {
            fill: black !important;
        }
        .st-emotion-cache-consg2.e16zdaao0 {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 2.5em;
            background-color: #333 !important;
            color: #fff !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
            font-size: 1em;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease, color 0.2s ease;
            text-decoration: none;
            padding: 0 1em;
        }
        .st-emotion-cache-consg2.e16zdaao0:hover {
            background-color: #444 !important;
            color: #fff !important;
            transform: scale(1.05);
        }
        .st-emotion-cache-consg2.e16zdaao0:active {
            background-color: #222 !important;
            color: #fff !important;
            transform: scale(0.95);
        }
        .st-emotion-cache-187vdiz.e1nzilvr4 {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            width: 100%;
            background-color: transparent !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .stButton>button {
            width: 100%;
            height: 2.5em;
            background-color: #333;
            color: #fff;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
            font-size: 1em;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease, color 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #444;
            color: #fff;
            transform: scale(1.05);
        }
        .stButton>button:active {
            background-color: #222;
            color: #fff;
            transform: scale(0.95);
        }
        </style>
        """, unsafe_allow_html=True)  # 按钮设置
    button_type = "secondary"

elif web_setting["web"]["button_style"] == "Simple-white":
    st.markdown("""
        <style>
        .st-emotion-cache-keje6w.e1f1d6gn3 {
            float: right !important;
            text-align: right !important;
            display: inline-block;
        }
        .st-emotion-cache-1vt4y43 {
            background-color:  white !important;
            color: black !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
        }
        .eyeqlp52.st-emotion-cache-1pbsqtx.ex0cdmw0 {
            fill: black !important;
        }
        .st-emotion-cache-consg2.e16zdaao0 {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 2.5em;
            background-color: white !important;
            color: black !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
            font-size: 1em;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease, color 0.2s ease;
            text-decoration: none;
            padding: 0 1em;
        }
        .st-emotion-cache-consg2.e16zdaao0:hover {
            background-color: #f0f0f0 !important;
            color: black !important;
            transform: scale(1.05);
        }
        .st-emotion-cache-consg2.e16zdaao0:active {
            background-color: #e0e0e0 !important;
            color: black !important;
            transform: scale(0.95);
        }
        .st-emotion-cache-187vdiz.e1nzilvr4 {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            width: 100%;
            background-color: transparent !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .stButton button {
            width: 100%;
            height: 2.5em;
            background-color: white !important;
            color: black !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
            font-size: 1em !important;
            cursor: pointer !important;
            transition: background-color 0.3s ease, transform 0.2s ease, color 0.2s ease;
            padding: 0.5em 1em !important;
        }
        .stButton button:hover {
            background-color: #f0f0f0 !important;
            color: black !important;
            transform: scale(1.05) !important;
        }
        .stButton button:active {
            background-color: #e0e0e0 !important;
            color: black !important;
            transform: scale(0.95) !important;
        }
        </style>
        """, unsafe_allow_html=True)  # 按钮设置
    button_type = "secondary"

elif web_setting["web"]["button_style"] == "Primary":
    button_type = "primary"
else:
    button_type = "secondary"

footer = """
<style>
.footer {
    position: fixed;
    bottom: 0;
    right: 0;
    padding: 10px;
    font-size: 14px;
    color: #555;
}
.footer p {
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
}
.footer a {
    color: #0073e6;
    text-decoration: none;
    transition: color 0.3s ease;
}
.footer a:hover {
    color: #005bb5;
}

/* Media query for mobile devices */
@media (max-width: 768px) {
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        left: 0;
        margin: 0 auto;
        width: 100%;
        background-color: white;
        border-top: 1px solid #ddd;
        justify-content: center;
        text-align: center;
    }
}
</style>
<div class="footer">
    <p><strong>Powered by <a href="https://zhile.io/" target="_blank">@Neo</a>，</strong> 
    <strong>Created by <a href="https://github.com/Chenyme" target="_blank">@Chenyme</a></strong></p>
</div>
"""

col1, col2, col3 = st.columns([0.32, 0.36, 0.32])
with col2:
    set_choose = sac.segmented(
        items=[
            sac.SegmentedItem(label='密码变更', icon='file-text'),
            sac.SegmentedItem(label='账户续费', icon='tools'),
        ], align='center', use_container_width=True, color='dark'
    )
    st.write("")
    st.write("")
    if set_choose == '密码变更':

        if "change" not in st.session_state:
            st.session_state.change = "password"

        with st.container(border=True):
            st.write("### 密码变更")
            st.write("")
            st.write("")

            if st.session_state.change == "password":

                user_account = st.text_input("**账户**", placeholder="您的账户", key="user_account1")
                user_password = st.text_input("**旧密码**", type="password", placeholder="您的旧密码", key="user_password1")
                user_password_new = st.text_input("**新密码**", type="password", placeholder="您的新密码", key="user_password_new1")

                st.divider()
                st.write("")
                if st.button("**立即更改**", use_container_width=True, type=button_type):
                    if user_account != "" and user_account is not None:
                        if user_password != "" and user_password is not None:
                            if user_password_new != "" and user_password_new is not None:
                                if user_account in config.keys():
                                    if user_password == config[user_account]['password']:
                                        if user_password_new != config[user_account]['password']:
                                            if len(user_password_new) >= 8:
                                                config[user_account]['password'] = user_password_new
                                                with open(current_path + '/config.json', 'w', encoding='utf-8') as file:
                                                    json.dump(config, file, indent=2)
                                                logger.info(
                                                    f"【密码更改】 账户：{user_account} 密码更改成功！new_password:{user_password}")
                                                st.toast('**密码已成功更改！**', icon=':material/check_circle:')
                                            else:
                                                st.toast('**密码长度不足，请填写8位及以上的密码！**', icon=':material/error:')
                                        else:
                                            st.toast('**修改失败，新密码不能与旧密码相同！**', icon=':material/error:')
                                    else:
                                        st.toast('**密码错误，请检查您填写的旧密码是否正确！**', icon=':material/error:')
                                else:
                                    st.toast('**账户不存在，请检查您填写的账户名称是否正确！**', icon=':material/error:')
                            else:
                                st.toast('**新密码不能为空，请填写您的新密码！**', icon=':material/error:')
                        else:
                            st.toast('**旧密码不能为空，请填写您的旧密码！**', icon=':material/error:')
                    else:
                        st.toast('**账户不能为空，请填写您的账户！**', icon=':material/error:')

                if st.button("**使用 UID 变更**", use_container_width=True, type=button_type):
                    st.session_state.change = "uid"
                    st.switch_page("pages/refresh.py")

            elif st.session_state.change == "uid":
                user_account = st.text_input("**账户**", placeholder="您的账户", key="user_account2")
                user_password = st.text_input("**新密码**", type="password", placeholder="您的新密码", key="user_password2")
                uid = st.text_input("**UID**", placeholder="你的唯一标识 - UID", key="uid")

                st.divider()
                st.write("")
                if st.button("**立即更改**", use_container_width=True, type=button_type):
                    if user_account != "" and user_account is not None:
                        if user_password != "" and user_password is not None:
                            if uid != "" and uid is not None:
                                if user_account in config.keys():
                                    if user_password != config[user_account]['password']:
                                        if len(user_password) >= 8:
                                            if config[user_account]['uid'] == uid:
                                                config[user_account]['password'] = user_password
                                                with open(current_path + '/config.json', 'w', encoding='utf-8') as file:
                                                    json.dump(config, file, indent=2)
                                                logger.info(f"【密码更改】 账户：{user_account} 密码更改成功！new_password:{user_password}")
                                                st.toast('**密码已成功更改！**', icon=':material/check_circle:')
                                            else:
                                                st.toast('**错误的UID，UID是您注册时和登陆时显示的令牌！**', icon=':material/error:')
                                        else:
                                            st.toast('**密码长度不足，请填写8位及以上的密码！**', icon=':material/error:')
                                    else:
                                        st.toast('**修改失败，新密码不能与旧密码相同！**', icon=':material/error:')
                                else:
                                    st.toast('**账户不存在，请检查您填写的账户名称是否正确！**', icon=':material/error:')
                            else:
                                st.toast('**UID不能为空，请填写您的UID！**', icon=':material/error:')
                        else:
                            st.toast('**密码不能为空，请填写您的密码！**', icon=':material/error:')
                    else:
                        st.toast('**账户不能为空，请填写您的账户！**', icon=':material/error:')

                if st.button("**使用密码变更**", use_container_width=True, type=button_type):
                    st.session_state.change = "password"
                    st.switch_page("pages/refresh.py")

            st.page_link("home.py", label="**:blue[返回首页]**")
            st.write("")
    else:
        if not web_setting["web"]["user_refresh"]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="display: flex; flex-direction: column; align-items: center;">
                        <img src="data:image/png;base64,{encoded_image}" alt="LOGO" style="width: 100px;">
                        <p style="text-align: center; color: gray; font-size: 12px; margin-top: -20px;">{version}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("")
                st.write("")
                sac.alert("**抱歉！出错啦！**",description="**管理员暂未开放相关功能！**", color="error", variant="filled", size="lg", radius="sm", icon=True)
                st.write("")
                st.write("")
                if st.button("**返回首页**", use_container_width=True, key="rf_home3", type=button_type):
                    st.switch_page("home.py")
                st.write("")
                st.write("")
        else:
            with st.container(border=True):
                st.write("### 账户续费")
                st.write("")
                st.write("")

                user_account = st.text_input("**账户**", placeholder="您的账户")
                user_password = st.text_input("**密码**", type="password", placeholder="您的密码")
                refresh = st.text_input("**刷新令牌**", placeholder="您的刷新令牌，输入后请Enter确认！")
                login_result, token_result, group_result = login(user_account, user_password)

                st.divider()
                st.write("")
                if st.button("**执行刷新**", use_container_width=True, type=button_type):
                    if user_account != "" and user_password != "":
                        if login_result == 2:
                            if refresh in refresh_data.keys():
                                if not refresh_data[refresh]['used']:
                                    if refresh_data[refresh]['group'] == group_result:
                                        refresh_token = accounts[group_result]['refresh_token']
                                        status, access_token = get_accesstoken(refresh_token)

                                        if status:
                                            accounts[group_result]['access_token'] = access_token
                                            with open(current_path + '/accounts.json', 'w', encoding='utf-8') as file:
                                                json.dump(accounts, file, indent=2)

                                            status, name, token_key = get_sharetoken(user_account, access_token, refresh_data[refresh]['site_limit'], refresh_data[refresh]["expires_in"], refresh_data[refresh]['gpt35_limit'], refresh_data[refresh]['gpt4_limit'], refresh_data[refresh]['show_conversations'])
                                            if status:
                                                config[user_account]['token'] = token_key
                                                config[user_account]['site_limit'] = refresh_data[refresh]['site_limit']
                                                config[user_account]['expires_in'] = refresh_data[refresh]['expires_in']
                                                config[user_account]['gpt35_limit'] = refresh_data[refresh]['gpt35_limit']
                                                config[user_account]['gpt4_limit'] = refresh_data[refresh]['gpt4_limit']
                                                config[user_account]['show_conversations'] = refresh_data[refresh]['show_conversations']

                                                with open(current_path + '/config.json', 'w', encoding='utf-8') as file:
                                                    json.dump(config, file, indent=2)

                                                refresh_data[refresh]['used'] = True
                                                with open(current_path + '/refresh.json', 'w', encoding='utf-8') as file:
                                                    json.dump(refresh_data, file, indent=2)

                                                logger.info(f"【账户续费】 账户：{user_account} 续费成功！续费:{refresh_data[refresh]['expires_in']}秒！")
                                                st.toast('续费成功！', icon=':material/check_circle:')
                                            else:
                                                logger.error(f"【账户续费】 账户：{user_account} 续费失败！请检查AC_Token是否有效！")
                                                st.toast('续费失败！请联系管理员更新相关Token！', icon=':material/error:')
                                        else:
                                            logger.error(f"【账户续费】 账户：{user_account} 续费失败！请检查RF_Token是否有效！")
                                            st.toast('续费失败！请联系管理员更新相关Token！', icon=':material/error:')
                                    else:
                                        st.toast('**验证失败，此刷新令牌与账户用户组不匹配！**', icon=':material/error:')
                                else:
                                    st.toast('**验证失败，此刷新令牌已被使用！**', icon=':material/error:')
                            else:
                                st.toast('**验证失败，此刷新令牌不存在！**', icon=':material/error:')
                        else:
                            st.toast('**验证失败，账户密码错误！**', icon=':material/error:')
                    else:
                        st.toast('**验证失败，账户密码不能为空！**', icon=':material/error:')

                if web_setting["web"]["refresh_link_enable"]:
                    st.link_button("**获取令牌**", web_setting["web"]["refresh_link"], use_container_width=True, type=button_type)

                st.page_link("home.py", label="**:blue[返回首页]**")
                st.write("")


st.logo("LOGO.png", link="https://github.com/Chenyme/oaifree-tools")
st.markdown(footer, unsafe_allow_html=True)  # 底部信息,魔改请勿删除