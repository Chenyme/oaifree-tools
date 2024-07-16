import os
import json
import toml
import time
import base64
import logging
import streamlit as st
import streamlit_antd_components as sac
from utils import get_accesstoken, get_sharetoken

version = "v1.2.1"

style_path = os.path.abspath('.') + '/style/'
current_path = os.path.abspath('.') + '/config/'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(current_path + "app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    web_setting = toml.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    accounts = json.load(file)
with open(current_path + '/users.json', 'r', encoding='utf-8') as file:
    users = json.load(file)
with open(current_path + '/openai.json', 'r', encoding='utf-8') as file:
    openai_data = json.load(file)
with open(current_path + '/anthropic.json', 'r', encoding='utf-8') as file:
    anthropic_data = json.load(file)
with open(current_path + '/refresh.json', 'r', encoding='utf-8') as file:
    refresh_data = json.load(file)
with open(style_path + "//Simple_White.html", "r", encoding="utf-8") as file:
    Simple_white_html = file.read()
with open(style_path + "//Classic_Black.html", "r", encoding="utf-8") as file:
    Classic_Black_html = file.read()
with open(style_path + "//Retro_Orange.html", "r", encoding="utf-8") as file:
    Retro_Orange_html = file.read()
    Retro_Orange_html = Retro_Orange_html.replace("{{text}}", "Discover opportunities")
with open(style_path + "//sidebar.html", "r", encoding="utf-8") as file:
    sidebar_html = file.read()
with open("LOGO.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

st.set_page_config(page_title=web_setting["web"]["title"], page_icon="LOGO.png", initial_sidebar_state=web_setting["web"]["sidebar_state"])


def authenticate(username, password):  # 验证用户
    account_name = users.get(username)
    return account_name and account_name['password'] == password


def login(username, password):  # 登录判断
    if username == web_setting['web']['super_user'] and password == web_setting['web']['super_key']:
        return 3
    elif username not in users:
        return 0
    elif authenticate(username, password):
        return 2
    else:
        return 1


with st.sidebar:
    st.write("")
    st.write("**服务面板**")

    @st.experimental_fragment
    def sider():
        st.page_link("pages/uid.py", label="UID 登录", use_container_width=True, icon=":material/badge:")
        st.page_link("pages/change.py", label="密码变更", use_container_width=True, icon=":material/change_circle:")
        st.page_link("pages/refresh.py", label="账户续费", use_container_width=True, icon=":material/history:")
        st.page_link("pages/share.py", label="免费使用", use_container_width=True, icon=":material/supervisor_account:")
        st.page_link("pages/admin.py", label="管理员登录", use_container_width=True, icon=":material/account_circle:")
    sider()

    st.divider()
    st.write("**更换主题**")
    st.write("")
    if st.button("Simple White"):
        st.session_state.theme = "Simple White"
    if st.button("Classic Black"):
        st.session_state.theme = "Classic Black"
    if st.button("Retro Orange"):
        st.session_state.theme = "Retro Orange"
    if st.session_state.theme == "Simple White":
        sidebar_html = sidebar_html.replace("#ffffff", "#f7f7f7")
        sidebar_html = sidebar_html.replace("#efede4", "#ffffff")
        st.markdown(sidebar_html, unsafe_allow_html=True)
    elif st.session_state.theme == "Classic Black":
        sidebar_html = sidebar_html.replace("border-radius: 15px;", "border-radius: 4px;")
        sidebar_html = sidebar_html.replace("#ffffff", "#f7f7f7")
        sidebar_html = sidebar_html.replace("#efede4", "#ffffff")
        st.markdown(sidebar_html, unsafe_allow_html=True)
    elif st.session_state.theme == "Retro Orange":
        st.markdown(sidebar_html, unsafe_allow_html=True)


if "theme" not in st.session_state:
    st.session_state.theme = web_setting["web"]["login_theme"]

if st.session_state.theme == "Simple White":
    st.markdown(Simple_white_html, unsafe_allow_html=True)
    st.markdown(f"<div class='centered-title'><h1>" + web_setting["web"]["title"] + "</h1></div><div class='centered-subtitle'><div>" + web_setting["web"]["subtitle"] + "</div></div>", unsafe_allow_html=True)
    st.write("")
    st.write("")

elif st.session_state.theme == "Classic Black":
    st.markdown(Classic_Black_html, unsafe_allow_html=True)
    st.markdown(f"<div class='centered-title'><h1>" + web_setting["web"]["title"] + "</h1></div><div class='centered-subtitle'><div>" + web_setting["web"]["subtitle"] + "</div></div>", unsafe_allow_html=True)
    st.write("")
    st.write("")

elif st.session_state.theme == "Retro Orange":
    st.markdown(Retro_Orange_html, unsafe_allow_html=True)

if st.session_state.theme == "Retro Orange":
    col1, col2, col3 = st.columns([0.12, 0.76, 0.12])
    with col2:
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
                st.error("""
                **抱歉，出错啦！**
                
                **管理员暂未开放相关功能！**
                """)
                st.write("")
                st.write("")
                if st.button("HomePage / 首页", use_container_width=True, key="rf_home3"):
                    st.switch_page("home.py")
                st.write("")
                st.write("")
        else:
            with st.container(border=True):
                st.markdown("""
                    <div style="text-align: center; font-family: 'Times New Roman', '宋体'; font-size: 30px;">
                        <p style="font-size: 25px;">Account Renewal</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.write("")

                user_account = st.text_input("**Account**", placeholder="Your Account / 您的账户", key="user_account1")
                user_password = st.text_input("**Password**", type="password", placeholder="Your Password / 您的密码", key="user_password1")
                refresh = st.text_input("**Refresh Token**", placeholder="Your Refresh Token / 您的令牌")
                login_result = login(user_account, user_password)

                st.write("")
                if st.button("Account Renewal / 续费", use_container_width=True):
                    if user_account != "" and user_password != "":
                        if login_result == 2:
                            if refresh in refresh_data.keys():
                                if not refresh_data[refresh]['used']:
                                    group_result = openai_data[user_account]['group']
                                    if refresh_data[refresh]['group'] == group_result:
                                        refresh_token = accounts[group_result]['refresh_token']
                                        status, access_token = get_accesstoken(refresh_token)

                                        if status:
                                            accounts[group_result]['access_token'] = access_token
                                            with open(current_path + '/accounts.json', 'w', encoding='utf-8') as file:
                                                json.dump(accounts, file, indent=2)

                                            status, name, token_key = get_sharetoken(user_account, access_token, refresh_data[refresh]['site_limit'], refresh_data[refresh]["expires_in"], refresh_data[refresh]['gpt35_limit'], refresh_data[refresh]['gpt4_limit'], refresh_data[refresh]['show_conversations'])
                                            if status:
                                                openai_data[user_account]['token'] = token_key
                                                openai_data[user_account]['site_limit'] = refresh_data[refresh]['site_limit']
                                                openai_data[user_account]['expires_in'] = refresh_data[refresh]['expires_in']
                                                openai_data[user_account]['gpt35_limit'] = refresh_data[refresh]['gpt35_limit']
                                                openai_data[user_account]['gpt4_limit'] = refresh_data[refresh]['gpt4_limit']
                                                openai_data[user_account]['show_conversations'] = refresh_data[refresh]['show_conversations']

                                                with open(current_path + '/openai.json', 'w', encoding='utf-8') as file:
                                                    json.dump(openai_data, file, indent=2)

                                                refresh_data[refresh]['used'] = True
                                                with open(current_path + '/refresh.json', 'w', encoding='utf-8') as file:
                                                    json.dump(refresh_data, file, indent=2)
                                                if str(refresh_data[refresh]['expires_in']) == "0":
                                                    logger.info(f"【账户续费】 账户：{user_account} 续费成功！续费:永久！")
                                                    st.toast('续费成功！', icon=':material/check_circle:')
                                                else:
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
                    st.link_button("Get Token / 获取", web_setting["web"]["refresh_link"], use_container_width=True)
                if st.session_state.theme == "Retro Orange":
                    st.page_link("home.py", label=":orange[HomePage / 首页]")
                else:
                    st.page_link("home.py", label="**返回首页**")
                st.write("")
else:
    col1, col2, col3 = st.columns([0.15, 0.7, 0.15])
    with col2:
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
                sac.alert("**抱歉！出错啦！**", description="**管理员暂未开放相关功能！**", color="error", variant="filled", size="lg", radius="md", icon=True)
                st.write("")
                st.write("")
                if st.button("**返回首页**", use_container_width=True, key="rf_home3"):
                    st.switch_page("home.py")
                st.write("")
                st.write("")
        else:
            with st.container(border=True):
                st.write("")
                st.markdown("""
                    <div style="text-align: center;">
                        <p style="font-size: 25px; font-weight: 700">账户续费</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.write("")
                st.write("")
                user_account = st.text_input("**账户**", placeholder="您的账户", key="user_account1")
                user_password = st.text_input("**密码**", type="password", placeholder="您的密码", key="user_password1")
                refresh = st.text_input("**刷新令牌**", placeholder="您的刷新令牌")
                login_result = login(user_account, user_password)

                st.write("")
                if st.button("**续费账户**", use_container_width=True):
                    if user_account != "" and user_password != "":
                        if login_result == 2:
                            if refresh in refresh_data.keys():
                                if not refresh_data[refresh]['used']:
                                    group_result = openai_data[user_account]['group']
                                    if refresh_data[refresh]['group'] == group_result:
                                        refresh_token = accounts[group_result]['refresh_token']
                                        status, access_token = get_accesstoken(refresh_token)

                                        if status:
                                            accounts[group_result]['access_token'] = access_token
                                            with open(current_path + '/accounts.json', 'w', encoding='utf-8') as file:
                                                json.dump(accounts, file, indent=2)
                                            status, name, token_key = get_sharetoken(user_account, access_token, refresh_data[refresh]['site_limit'], refresh_data[refresh]["expires_in"], refresh_data[refresh]['gpt35_limit'], refresh_data[refresh]['gpt4_limit'], refresh_data[refresh]['show_conversations'])
                                            if status:
                                                openai_data[user_account]['token'] = token_key
                                                openai_data[user_account]['site_limit'] = refresh_data[refresh]['site_limit']
                                                openai_data[user_account]['expires_in'] = refresh_data[refresh]['expires_in']
                                                openai_data[user_account]['gpt35_limit'] = refresh_data[refresh]['gpt35_limit']
                                                openai_data[user_account]['gpt4_limit'] = refresh_data[refresh]['gpt4_limit']
                                                openai_data[user_account]['show_conversations'] = refresh_data[refresh]['show_conversations']

                                                with open(current_path + '/openai.json', 'w', encoding='utf-8') as file:
                                                    json.dump(openai_data, file, indent=2)

                                                refresh_data[refresh]['used'] = True
                                                with open(current_path + '/refresh.json', 'w', encoding='utf-8') as file:
                                                    json.dump(refresh_data, file, indent=2)

                                                if str(refresh_data[refresh]['expires_in']) == "0":
                                                    logger.info(f"【账户续费】 账户：{user_account} 续费成功！续费:永久！")
                                                    st.toast('续费成功！', icon=':material/check_circle:')
                                                else:
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
                    st.link_button("Get Token / 获取", web_setting["web"]["refresh_link"], use_container_width=True)
                if st.session_state.theme == "Retro Orange":
                    st.page_link("home.py", label=":orange[Return HomePage / 首页]")
                else:
                    st.page_link("home.py", label="**返回首页**")
                st.write("")

with open(style_path + "//footer.html", "r", encoding="utf-8") as file:
    footer_html = file.read()
    color = "white"
    if st.session_state.theme == "Retro Orange":
        color = "#efede4"
    footer_html = footer_html.replace("{{color}}", color)
st.markdown(footer_html, unsafe_allow_html=True)
st.logo("LOGO.png", link="https://github.com/Chenyme/oaifree-tools")