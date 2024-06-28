import os
import toml
import logging
import json
import streamlit as st
import streamlit_antd_components as sac
from utils import get_sharetoken, get_accesstoken, get_login_url


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

current_path = os.path.abspath('.') + '/config'
with open(current_path + '/invite.json', 'r', encoding='utf-8') as file:
    invite_config = json.load(file)
with open(current_path + '/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    accounts = json.load(file)
with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    web_setting = toml.load(file)
with open(current_path + '/share.json', 'r', encoding='utf-8') as file:
    share_data = json.load(file)

st.set_page_config(layout="wide", page_title=web_setting["web"]["title"], page_icon="LOGO.png")

if "role" not in st.session_state:
    st.session_state.role = None


@st.experimental_dialog("成为我们的新伙伴！")  # 注册模块
def select():
    st.write("")
    st.write("")
    user_new_acc = st.text_input("**账户：**")
    user_new_pass = st.text_input("**密码：**")
    user_new_invite = st.text_input("**注册邀请码：**")
    st.write("")
    st.write("")
    if st.button("**加入**", use_container_width=True, type="primary"):
        st.write("")
        if user_new_acc == "":
            st.error("请填写您的账户!", icon=":material/error:")
        elif user_new_pass == "":
            st.error("请填写您的密码!", icon=":material/error:")
        elif user_new_acc in config:
            st.error("该账户已存在!", icon=":material/error:")
        elif user_new_invite not in invite_config.keys():
            st.error("此注册邀请码无效，请重新输入！", icon=":material/error:")
        else:
            user_new_group = invite_config[user_new_invite]
            group_data = accounts[user_new_group]
            acc = group_data['access_token']
            new_name, new_token_key = get_sharetoken(user_new_acc, acc, web_setting["web"]["site_limit"], web_setting["web"]["expires_in"], web_setting["web"]["gpt35_limit "], web_setting["web"]["gpt4_limit "], web_setting["web"]["show_conversations"])

            json_data = {
                new_name: {
                    'password': user_new_pass,
                    'token': new_token_key,
                    'group': user_new_group,
                    'type': group_data['account_type'],
                    'site_limit': web_setting["web"]["site_limit"],
                    'expires_in': web_setting["web"]["expires_in"],
                    'gpt35_limit': web_setting["web"]["gpt35_limit"],
                    'gpt4_limit': web_setting["web"]["gpt4_limit"],
                    'show_conversations': web_setting["web"]["show_conversations"]
                }
            }
            config.update(json_data)

            config_json = json.dumps(config, indent=2, ensure_ascii=False)
            with open(current_path + 'config.json', 'w', encoding='utf-8') as json_file:
                json_file.write(config_json)
            logger.info(f"<用户> 【用户注册】 新用户注册成功！name：{new_name}，token:{new_token_key}，group:{user_new_group}，注册邀请码：{user_new_invite}")
            st.success("注册成功，3s后自动刷新界面！", icon=":material/check_circle")
            st.rerun()
    st.write("")


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


# 应用页面样式
st.write("")
st.write("")
st.markdown("<div style='text-align:center;'><h1 style='text-align:center;'>" + web_setting["web"]["title"] + "</h1></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'><div>" + web_setting["web"]["subtitle"] + "</div></div>", unsafe_allow_html=True)

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 2.5em;
        background-color: #333;
        color: #fff;
        border: none;
        border-radius: 10px;
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


col4, col5, col6 = st.columns([0.3, 0.23, 0.3])
with col4:
    col1, col2, col3 = st.columns([0.01, 0.69, 0.3])
    with col2:
        if web_setting["web"]["notice_enable"]:
            sac.alert(label=web_setting["web"]["notice_title"], description=web_setting["web"]["notice_subtitle"], color=web_setting["web"]["notice_color"],
                      variant=web_setting["web"]["notice_style"], banner=web_setting["web"]["notice_banner"], size=web_setting["web"]["notice_size"], radius=web_setting["web"]["notice_radius"], icon=True, closable=True)
with col5:
    st.write("")
    st.write("")
    st.write("")
    account = st.text_input("**账户**")
    password = st.text_input("**密码**", type="password")
    st.write("---")
    if st.button("**登录**", use_container_width=True):
        login_result, token_result, group_result = login(account, password)
        if login_result == 0:
            st.toast('**此账户不存在或已被封禁！**', icon=':material/error:')
        elif login_result == 1:
            st.toast('**账户密码错误，请重新输入！**', icon=':material/error:')
        elif login_result == 2:
            domain = web_setting["web"]["domain"]
            url = get_login_url(domain, token_result)
            logger.info(f"【用户登录】 用户：{account} 登录成功！")
            st.toast('获取登录信息成功!', icon=':material/check_circle:')
            if web_setting["web"]["refresh_all"]:
                user_ac_tk = get_accesstoken(accounts[group_result]["refresh_token"])
                if user_ac_tk is None or user_ac_tk == "":
                    logger.info(f"<用户> 【AC刷新】 用户登录时，{group_result} 的Access_token刷新失败！")
                else:
                    accounts[group_result]["access_token"] = user_ac_tk
                    accounts_json = json.dumps(accounts, indent=2)
                    json_filename = 'accounts.json'
                    with open(current_path + json_filename, 'w', encoding='utf-8') as json_file:
                        json_file.write(accounts_json)
                    logger.info(f"<用户> 【AC刷新】 用户登录时 {group_result} 的Access_token刷新成功！")
        elif login_result == 3:
            st.session_state.role = "admin"
            logger.info(f"【管理登录】 管理员：{account} 登录成功！")
            st.page_link("pages/admin.py", label="管理面板", icon=":material/admin_panel_settings:", use_container_width=True)

    if st.button("**注册**", use_container_width=True):
        select()

    try:
        st.link_button("**点我验证**", url, use_container_width=True, type="primary")
    except:
        pass
    st.write("")
    st.page_link("pages/refresh.py", label=":red[无法登录？]", icon=":material/login:", use_container_width=True)

    st.page_link("pages/share.py", label="Share共享站", icon=":material/login:", use_container_width=True)

    footer = """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #555;
        }
        .footer a {
            color: #0073e6;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        .footer a:hover {
            color: #005bb5;
        }
        </style>
        <div class="footer">
            <p><strong>Powered by <a href="https://zhile.io/" target="_blank">@Neo</a>, </strong> 
            <strong>Created by <a href="https://github.com/Chenyme" target="_blank">@Chenyme</a></strong></p>
        </div>
        """

    st.markdown(footer, unsafe_allow_html=True)
