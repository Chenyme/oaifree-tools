import os
import json
import toml
import time
import base64
import logging
import streamlit as st

version = "v1.2.1"

style_path = os.path.abspath('.') + '/style/'
current_path = os.path.abspath('.') + '/config/'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(current_path + "app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

with open(current_path + '/invite.json', 'r', encoding='utf-8') as file:
    invite_config = json.load(file)
with open(current_path + '/users.json', 'r', encoding='utf-8') as file:
    users = json.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    accounts = json.load(file)
with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    web_setting = toml.load(file)
with open(current_path + '/refresh.json', 'r', encoding='utf-8') as file:
    refresh_data = json.load(file)
with open("LOGO.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()
with open(current_path + '/anthropic.json', 'r', encoding='utf-8') as file:
    anthropic_data = json.load(file)
with open(style_path + "//Simple_White.html", "r", encoding="utf-8") as file:
    Simple_white_html = file.read()
with open(style_path + "//Classic_Black.html", "r", encoding="utf-8") as file:
    Classic_Black_html = file.read()
with open(style_path + "//Retro_Orange.html", "r", encoding="utf-8") as file:
    Retro_Orange_htm = file.read()
    Retro_Orange_htm = Retro_Orange_htm.replace("{{text}}", "Analyze complex data")
with open(style_path + "//sidebar.html", "r", encoding="utf-8") as file:
    sidebar_html = file.read()

if "theme" not in st.session_state:
    st.session_state.theme = web_setting["web"]["login_theme"]


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


st.set_page_config(page_title=web_setting["web"]["title"], page_icon="LOGO.png", initial_sidebar_state=web_setting["web"]["sidebar_state"])

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
    st.markdown(Retro_Orange_htm, unsafe_allow_html=True)

if "change" not in st.session_state:
    st.session_state.change = "password"

if st.session_state.theme == "Retro Orange":
    col1, col2, col3 = st.columns([0.12, 0.76, 0.12])
    with col2:
        with st.container(border=True):
            @st.experimental_fragment
            def change_area():
                if st.session_state.change == "password":
                    st.markdown("""
                        <div style="text-align: center; font-family: 'Times New Roman', '宋体'; font-size: 30px;">
                            <p style="font-size: 25px;">Password Change</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.write("")

                    user_account = st.text_input("**Account**", placeholder="Your Account / 您的帐户", key="user_account1")
                    user_password = st.text_input("**Old Password**", type="password", placeholder="Your Old Password / 您的旧密码", key="user_password1")
                    user_password_new = st.text_input("**New Password**", type="password", placeholder="Your New Password / 您的新密码", key="user_password_new1")

                    st.write("")
                    if st.button("Click For Change / 变更", use_container_width=True):
                        if user_account != "" and user_account is not None:
                            if user_password != "" and user_password is not None:
                                if user_password_new != "" and user_password_new is not None:
                                    if user_account in users.keys():
                                        if user_password == users[user_account]['password']:
                                            if user_password_new != users[user_account]['password']:
                                                if len(user_password_new) >= 8:
                                                    users[user_account]['password'] = user_password_new
                                                    with open(current_path + '/users.json', 'w', encoding='utf-8') as file:
                                                        json.dump(users, file, indent=2)
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

                    if st.button("Change With UID / 用 UID 更改", use_container_width=True):
                        time.sleep(0.05)
                        st.session_state.change = "uid"
                        st.switch_page("pages/change.py")

                elif st.session_state.change == "uid":

                    st.markdown("""
                        <div style="text-align: center; font-family: 'Times New Roman', '宋体'; font-size: 30px;">
                            <p style="font-size: 25px;">Password Change</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.write("")
                    user_account = st.text_input("**Account**", placeholder="Your Account / 您的账户", key="user_account1")
                    user_password = st.text_input("**New Password**", type="password", placeholder="Your New Password / 您的新密码", key="user_password1")
                    uid = st.text_input("**UID**", placeholder="Your UID / 您的UID", key="uid")

                    st.write("")
                    if st.button("Click For Change / 变更", use_container_width=True):
                        if user_account != "" and user_account is not None:
                            if user_password != "" and user_password is not None:
                                if uid != "" and uid is not None:
                                    if user_account in users.keys():
                                        if user_password != users[user_account]['password']:
                                            if len(user_password) >= 8:
                                                if users[user_account]['uid'] == uid:
                                                    users[user_account]['password'] = user_password
                                                    with open(current_path + '/users.json', 'w', encoding='utf-8') as file:
                                                        json.dump(users, file, indent=2)
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

                    if st.button("Change With Password / 用 密码 更改", use_container_width=True):
                        time.sleep(0.05)
                        st.session_state.change = "password"
                        st.switch_page("pages/change.py")
                st.page_link("home.py", label=":orange[HomePage / 首页]")
            change_area()
            st.write("")
else:
    col1, col2, col3 = st.columns([0.15, 0.7, 0.15])
    with col2:
        @st.experimental_fragment
        def change_area_old():
            with st.container(border=True):
                if st.session_state.change == "password":
                    st.markdown("""
                        <div style="text-align: center; font-size: 30px; font-weight: 700;">
                            <p style="font-size: 25px; font-weight: 700;">密码变更</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.write("")

                    user_account = st.text_input("**帐户**", placeholder="您的帐户", key="user_account")
                    user_password = st.text_input("**旧密码**", type="password", placeholder="您的旧密码", key="user_password")
                    user_password_new = st.text_input("**新密码**", type="password", placeholder="您的新密码", key="user_password_new")

                    st.write("")
                    if st.button("**变更**", use_container_width=True):
                        if user_account != "" and user_account is not None:
                            if user_password != "" and user_password is not None:
                                if user_password_new != "" and user_password_new is not None:
                                    if user_account in users.keys():
                                        if user_password == users[user_account]['password']:
                                            if user_password_new != users[user_account]['password']:
                                                if len(user_password_new) >= 8:
                                                    users[user_account]['password'] = user_password_new
                                                    with open(current_path + '/users.json', 'w', encoding='utf-8') as file:
                                                        json.dump(users, file, indent=2)
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

                    if st.button("**使用 UID 更改**", use_container_width=True):
                        time.sleep(0.05)
                        st.session_state.change = "uid"
                        st.switch_page("pages/change.py")

                elif st.session_state.change == "uid":

                    st.markdown("""
                        <div style="text-align: center; font-size: 30px; font-weight: 700;">
                            <p style="font-size: 25px; font-weight: 700;">密码变更</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.write("")
                    user_account = st.text_input("**账户**", placeholder="您的账户", key="user_account")
                    user_password = st.text_input("**新密码**", type="password", placeholder="新密码", key="user_password")
                    uid = st.text_input("**UID**", placeholder="您的UID", key="uid")

                    st.write("")
                    if st.button("**变更**", use_container_width=True):
                        if user_account != "" and user_account is not None:
                            if user_password != "" and user_password is not None:
                                if uid != "" and uid is not None:
                                    if user_account in users.keys():
                                        if user_password != users[user_account]['password']:
                                            if len(user_password) >= 8:
                                                if users[user_account]['uid'] == uid:
                                                    users[user_account]['password'] = user_password
                                                    with open(current_path + '/users.json', 'w', encoding='utf-8') as file:
                                                        json.dump(users, file, indent=2)
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

                    if st.button("**用 密码 更改**", use_container_width=True):
                        st.session_state.change = "password"
                        time.sleep(0.05)
                        st.switch_page("pages/change.py")
                st.page_link("home.py", label="**返回首页**")
                st.write("")
        change_area_old()
