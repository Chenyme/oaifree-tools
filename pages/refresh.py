import json
import toml
import os
import logging
import streamlit as st
from utils import get_accesstoken, get_sharetoken, login

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log", encoding='utf-8'),
                              logging.StreamHandler()])

logger = logging.getLogger()

png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

current_path = os.path.abspath('.')
with open(current_path + '/invite.json', 'r', encoding='utf-8') as file:
    invite_config = json.load(file)
with open(current_path + '/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    accounts = json.load(file)
with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    web_setting = toml.load(file)


st.set_page_config(layout="wide", page_title=web_setting["web"]["title"], page_icon="LOGO.png")


st.markdown("""
    <style>
    .stButton>button {
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
    """, unsafe_allow_html=True)
st.title("")
st.write("")
st.write("")
st.write("")
col1, col2, col3 = st.columns(3)
with col2:
    with st.container(border=True):
        if not web_setting["web"]["user_refresh"]:
            st.error("""
            ---
            ### 出错啦！
            ##### 管理员暂未开放相关功能。
            ##### 无法登录请联系管理员！
            ##### 忘记密码请联系管理员！
            ---
            """)

        if web_setting["web"]["user_refresh"]:
            st.write("### 账户刷新")
            st.write("")
            st.write("")

            user_account = st.text_input("**账户**")
            user_password = st.text_input("**密码**", type="password")
            login_result, token_result, group_result = login(user_account, user_password)
            st.write("")
            st.write("")
            if st.button("**刷新状态**", use_container_width=True, type="primary"):
                if user_account != "" and user_password != "":
                    if login_result:
                        user_re_tk = accounts[group_result]["refresh_token"]
                        user_ac_tk = get_accesstoken(user_re_tk)
                        if user_ac_tk is None:
                            st.toast("刷新失败，请联系管理员检查相关配置！", icon=':material/error:')
                        else:
                            name, user_share_token = get_sharetoken(user_account, user_ac_tk)
                            if user_share_token == token_result:
                                accounts[group_result]["access_token"] = user_ac_tk
                                acoounts_json = json.dumps(accounts, indent=2)
                                json_filename = 'accounts.json'
                                with open(json_filename, 'w', encoding='utf-8') as json_file:
                                    json_file.write(acoounts_json)
                                st.toast("刷新成功!", icon=':material/check_circle')
                            else:
                                st.toast("刷新失败，请联系管理员!", icon=':material/error:')
                    else:
                        st.toast('验证失败，请检查您的账户密码!', icon=':material/error:')
                else:
                    st.toast('请输入正确的账户密码!', icon=':material/error:')
            st.write("")
            if st.button("**返回首页**", use_container_width=True):
                st.switch_page("home.py")
            st.write("")