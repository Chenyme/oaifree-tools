import json
import toml
import os
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

st.markdown("""
    <style>
    .st-emotion-cache-consg2.e16zdaao0 {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        height: 2.5em;
        background-color: #333 !important;
        color: #fff !important;
        border: none;
        border-radius: 10px;
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
    </style>
    """, unsafe_allow_html=True)  # 链接按钮样式

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
col1, col2, col3 = st.columns(3)
with col2:
    with st.container(border=True):
        if not web_setting["web"]["user_refresh"]:
            col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
            with col2:
                st.image("LOGO.png", width=200, use_column_width=True)
            sac.alert("**诶呀！出错啦！**",description="**管理员暂未开放相关功能！**", color="error", variant="filled", size="lg", radius="lg", icon=True, closable=True)
            st.write("")
            if st.button("**返回首页**", use_container_width=True):
                st.switch_page("home.py")
            st.write("")

        else:
            st.write("### 账户刷新")
            st.write("")
            st.write("")

            user_account = st.text_input("**账户**")
            user_password = st.text_input("**密码**", type="password")
            refresh = st.text_input("**刷新令牌**")
            login_result, token_result, group_result = login(user_account, user_password)
            st.write("")
            st.write("")
            if st.button("**执行刷新**", use_container_width=True):
                if user_account != "" and user_password != "":
                    if login_result == 2:
                        if refresh in refresh_data.keys():
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

                                        del refresh_data[refresh]
                                        with open(current_path + '/refresh.json', 'w', encoding='utf-8') as file:
                                            json.dump(refresh_data, file, indent=2)

                                        logger.info(f"【账户刷新】 账户：{user_account} 刷新成功！")
                                        st.toast('刷新成功！', icon=':material/check:')
                                    else:
                                        logger.error(f"【账户刷新】 账户：{user_account} 刷新失败！请检查AC_Token是否有效！")
                                        sac.alert("刷新失败！请联系管理员！", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
                                else:
                                    logger.error(f"【账户刷新】 账户：{user_account} 刷新失败！请检查RF_Token是否有效！")
                                    sac.alert("刷新失败！请联系管理员！", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
                            else:
                                sac.alert("刷新令牌与账户不匹配！请联系管理员更换！", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
                        else:
                            sac.alert("刷新令牌无效！", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
                    else:
                        sac.alert("账户密码错误！", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
                else:
                    sac.alert("账户密码不能为空！", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)

            if web_setting["web"]["refresh_link_enable"]:
                st.link_button("**获取刷新令牌**", web_setting["web"]["refresh_link"], use_container_width=True)

            st.write("")
            if st.button("**返回首页**", use_container_width=True, key="rf_home"):
                st.switch_page("home.py")
col4, col5, col6 = st.columns([0.3, 0.23, 0.3])
with col5:
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