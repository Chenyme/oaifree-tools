import os
import toml
import logging
import json
import streamlit as st
import secrets
import streamlit_antd_components as sac
from utils import get_sharetoken, get_accesstoken, get_oaifree_login_url, check_sharetoken, get_fucladue_login_url

style_path = os.path.abspath('.') + '/style/'
current_path = os.path.abspath('.') + '/config/'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(current_path + "app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:  # web设置
    web_setting = toml.load(file)
with open(current_path + '/users.json', 'r', encoding='utf-8') as file:  # 用户数据
    users = json.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:  # 账户数据
    accounts = json.load(file)
with open(current_path + '/domain.json', 'r', encoding='utf-8') as file:  # 域名数据
    domains = json.load(file)
with open(current_path + '/openai.json', 'r', encoding='utf-8') as file:  # OpenAI数据
    openai_data = json.load(file)
with open(current_path + '/anthropic.json', 'r', encoding='utf-8') as file:  # Anthropic数据
    anthropic_data = json.load(file)
with open(current_path + '/invite.json', 'r', encoding='utf-8') as file:  # OpenAI邀请数据
    invite_config = json.load(file)
with open(style_path + "//Simple_White.html", "r", encoding="utf-8") as file:  # 网页样式
    Simple_white_html = file.read()
with open(style_path + "//Classic_Black.html", "r", encoding="utf-8") as file:
    Classic_Black_html = file.read()
with open(style_path + "//Retro_Orange.html", "r", encoding="utf-8") as file:
    Retro_Orange_html = file.read()
    Retro_Orange_html = Retro_Orange_html.replace("{{text}}", "Deepen understanding")
with open(style_path + "//sidebar.html", "r", encoding="utf-8") as file:
    sidebar_html = file.read()


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


def check_openai(token_result, user_name, group_result):

    error_status = False
    with st.status("**正在验证您的环境...**") as status:
        if check_sharetoken(token_result):
            st.session_state.role = None
            token_result = token_result
        else:
            st.session_state.role = None
            if web_setting["web"]["refresh_all"]:
                if str(openai_data[user_name]["expires_in"]) == "0":
                    status.update(label="**SA状态已失效！尝试刷新中...**", state="running", expanded=True)
                    logger.error(f"【用户登录】 用户：{user_name} SA状态已失效！")
                    sa_status, name, token_result = get_sharetoken(
                        user_name,
                        accounts[group_result]["access_token"],
                        openai_data[user_name]["site_limit"],
                        openai_data[user_name]["expires_in"],
                        openai_data[user_name]["gpt35_limit"],
                        openai_data[user_name]["gpt4_limit"],
                        openai_data[user_name]["show_conversations"])

                    if sa_status:
                        logger.info(f"【用户登录】 用户：{user_name} SA状态刷新成功！")
                        openai_data[user_name]["token"] = token_result
                        config_json = json.dumps(openai_data, indent=2)
                        with open(current_path + 'openai.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(config_json)
                    else:
                        status.update(label="**AC状态已失效！尝试刷新中...**", state="running", expanded=False)
                        logger.error(f"【用户登录】 用户组：{group_result} AC状态已失效！")
                        ac_status, user_ac_token = get_accesstoken(accounts[group_result]["refresh_token"])
                        if ac_status:
                            logger.info(f"【用户登录】 用户组：{group_result} AC状态刷新成功！")
                            status.update(label="**即将完成！请耐心等待...**", state="running", expanded=False)
                            sa_status, name, token_result = get_sharetoken(
                                user_name,
                                user_ac_token,
                                openai_data[user_name]["site_limit"],
                                openai_data[user_name]["expires_in"],
                                openai_data[user_name]["gpt35_limit"],
                                openai_data[user_name]["gpt4_limit"],
                                openai_data[user_name]["show_conversations"])
                            logger.info(f"【用户登录】 用户：{user_name} SA状态刷新成功！")
                            openai_data[user_name]["token"] = token_result
                            config_json = json.dumps(openai_data, indent=2)
                            accounts[group_result]["access_token"] = user_ac_token
                            accounts_json = json.dumps(accounts, indent=2)
                            with open(current_path + 'openai.json', 'w', encoding='utf-8') as json_file:
                                json_file.write(config_json)
                            with open(current_path + 'accounts.json', 'w', encoding='utf-8') as json_file:
                                json_file.write(accounts_json)
                        else:
                            logger.error(f"【用户登录】 用户组：{group_result} AC状态刷新失败！")
                            error_status = "RF过期"
                else:
                    error_status = "过期"
            else:
                error_status = "SA过期"
        status.update(label="**环境验证成功！**", state="complete", expanded=False)
    return error_status, token_result


def check_anthropic(token_result, user_name):  # 看看始皇后续有没有大动作啦!
    return False, False


@st.experimental_dialog("成为我们的新伙伴！")  # 注册模块
def select():
    st.write("")
    if st.session_state.theme == "Retro Orange":
        user_new_acc = st.text_input("**New Account：**", placeholder="name@yourcompany.com / 账户")
        user_new_pass = st.text_input("**New Password：**", type="password", placeholder="your password / 密码")
        user_new_invite = st.text_input("**Invite Token：**", placeholder="your invite token. Press Enter To Apply / 邀请令牌")
        button_1 = "Join Us / 注册"
        button_2 = "Get Token / 获取"
    else:
        user_new_acc = st.text_input("**账户：**", placeholder="您的账户")
        user_new_pass = st.text_input("**密码：**", type="password", placeholder="您的密码")
        user_new_invite = st.text_input("**邀请令牌：**", placeholder="您的邀请令牌，输入后请Enter确认！")
        button_1 = "**注册账户**"
        button_2 = "****获取令牌****"

    st.write("")
    if web_setting["web"]["invite_link_enable"]:
        st.link_button(f"{button_2}", web_setting["web"]["invite_link"], use_container_width=True)

    if st.button(f"{button_1}", use_container_width=True):
        uid = "UID-" + secrets.token_urlsafe(32)
        if user_new_acc == "":
            st.error("**请填写您的账户！**", icon=":material/error:")
        elif user_new_pass == "":
            st.error("**请填写您的密码！**", icon=":material/error:")
        elif len(user_new_pass) < 8:
            st.error("**密码长度至少为8位！**", icon=":material/error:")
        elif user_new_acc in users.keys():
            st.error("**此账户已存在！**", icon=":material/error:")
        elif user_new_invite not in invite_config.keys():
            st.error("**邀请令牌无效！**", icon=":material/error:")
        elif invite_config[user_new_invite]['used']:
            st.error("**邀请令牌已被使用！**", icon=":material/error:")
        else:
            if invite_config[user_new_invite]['chatgpt']:
                user_openai_group = invite_config[user_new_invite]['openai-group']
                acc = accounts[user_openai_group]['access_token']
                status, new_name, new_token_key = get_sharetoken(user_new_acc, acc, invite_config[user_new_invite]['site_limit'], invite_config[user_new_invite]["expires_in"], invite_config[user_new_invite]["gpt35_limit"], invite_config[user_new_invite]["gpt4_limit"], invite_config[user_new_invite]["show_conversations"])
                if status:
                    st.session_state.signup2 = True
                    json_data_2 = {
                        user_new_acc: {
                            'token': new_token_key,
                            'group': invite_config[user_new_invite]['openai-group'],
                            'type': accounts[user_openai_group]['account_type'],
                            'site_limit': invite_config[user_new_invite]['site_limit'],
                            'expires_in': invite_config[user_new_invite]['expires_in'],
                            'gpt35_limit': invite_config[user_new_invite]['gpt35_limit'],
                            'gpt4_limit': invite_config[user_new_invite]['gpt4_limit'],
                            'show_conversations': invite_config[user_new_invite]['show_conversations']
                        }
                    }
                    openai_data.update(json_data_2)
                    config_json = json.dumps(openai_data, indent=2)
                    with open(current_path + 'openai.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(config_json)
                else:
                    with col6:
                        st.error(f"**新增失败，请联系管理员检查 AC 状态！**", icon=":material/error:")
                        logger.error(f"【用户注册】 用户：{user_new_acc} 注册失败！{user_openai_group} AC状态异常！")
            else:
                st.session_state.signup2 = True

            if invite_config[user_new_invite]['claude'] and "signup2" in st.session_state:
                user_claude_group = invite_config[user_new_invite]['anthropic-group']
                json_data_3 = {
                    user_new_acc: {
                        'token': accounts[user_claude_group]['access_token'],
                        'group': user_claude_group,
                        'type': accounts[user_claude_group]['account_type']
                    }
                }
                anthropic_data.update(json_data_3)
                anthropic_datas = json.dumps(anthropic_data, indent=2)
                with open(current_path + 'anthropic.json', 'w', encoding='utf-8') as json_file:
                    json_file.write(anthropic_datas)

            if "signup2" in st.session_state:
                json_data_1 = {
                    user_new_acc: {
                        'password': user_new_pass,
                        'uid': uid,
                        'allow_chatgpt': invite_config[user_new_invite]['chatgpt'],
                        'allow_claude': invite_config[user_new_invite]['claude'],
                        'note': invite_config[user_new_invite]['note'],
                    }
                }
                users.update(json_data_1)
                user_datas = json.dumps(users, indent=2)
                with open(current_path + 'users.json', 'w', encoding='utf-8') as json_file:
                    json_file.write(user_datas)
                del st.session_state.signup2
                invite_config[user_new_invite]['used'] = True
                invite_datas = json.dumps(invite_config, indent=2)
                with open(current_path + 'invite.json', 'w', encoding='utf-8') as json_file:
                    json_file.write(invite_datas)
                logger.info(f"【用户注册】 用户：{user_new_acc} 注册成功！")
                st.success(f"**注册成功！请牢记您的 UID! (4+32位)**", icon=":material/check_circle:")
                st.success(f"**{uid}**")


@st.experimental_dialog("身份验证")
def choose(user_name):
    del st.session_state["role"]
    st.write(f"**欢迎！{user_name}，请牢记您的 UID:**")
    st.write(f"**{users[user_name]['uid']}**")
    st.write("")
    st.write("")
    if users[user_name]["allow_chatgpt"]:
        openai_token = openai_data[user_name]["token"]
        group_result = openai_data[user_name]["group"]
        openai_error_status, openai_token = check_openai(openai_token, user_name, group_result)  # 查询状态
    else:
        openai_error_status = True
    if users[user_name]["allow_claude"]:
        anthropic_token = anthropic_data[user_name]["token"]
        anthropic_error_status, anthropic_token = check_anthropic(anthropic_token, user_name)  # 查询状态，暂无实质性检测
    else:
        anthropic_error_status = True

    with st.status("**正在验证您的身份...**") as status:
        if users[user_name]["allow_chatgpt"]:
            if openai_error_status == "RF过期":
                status.update(label="** RF 验证失败！**", state="error", expanded=True)
                st.write("")
                st.error("**OpenAI 验证失败，请联系管理员更换 RF！**", icon=":material/error:")
            elif openai_error_status == "过期":
                status.update(label="**账户状态已失效！**", state="error", expanded=True)
                st.write("")
                st.error("**OpenAI 账户已过期，请联系管理员续费！**", icon=":material/error:")
            elif openai_error_status == "SA过期":
                status.update(label="** AC 验证失败！**", state="error", expanded=True)
                st.write("")
                st.error("**OpenAI 验证失败，请联系管理员更换 AC！**", icon=":material/error:")
            elif not openai_error_status:
                status.update(label="**检测服务连通性...**", state="running", expanded=False)

        if users[user_name]["allow_claude"]:
            if not anthropic_error_status:
                status.update(label="**检测服务连通性...**", state="running", expanded=False)

        if web_setting["domain"]["choose_domain"] == "不允许":
            logger.info(f"【用户登录】 用户：{user_name} 登录成功！")
            if users[user_name]["allow_chatgpt"]:
                if not openai_error_status:
                    openai_domain = web_setting["domain"]["domain_default_openai"]
                    if domains[openai_domain]['type'] == "Pandora":
                        openai_url = "https://" + openai_domain + "/auth/login_share?token=" + openai_token
                    else:
                        openai_url = get_oaifree_login_url(openai_domain, openai_token)
                    st.write("")
                    if openai_url:  # 判断是否有链接
                        st.link_button("**ChatGPT**", openai_url, use_container_width=True)
                        status.update(label="**用户验证成功!**", state="complete", expanded=True)
                    else:
                        st.error("**ChatGPT 连接失败！**", icon=":material/error:")
                        status.update(label="**ChatGPT 连接失败！**", state="error", expanded=True)

            if users[user_name]["allow_claude"]:
                if not anthropic_error_status:
                    anthropic_domain = web_setting["domain"]["domain_default_anthropic"]
                    anthropic_token = anthropic_data[user_name]["token"]
                    anthropic_url = get_fucladue_login_url(anthropic_domain, anthropic_token, user_name)
                    st.write("")
                    if anthropic_url:  # 判断是否有链接
                        st.link_button("**Claude**", f"https://{anthropic_domain}{anthropic_url}", use_container_width=True)
                        status.update(label="**用户验证成功!**", state="complete", expanded=True)
                    else:
                        st.error("**Claude 连接失败！**", icon=":material/error:")
                        status.update(label="**Claude 连接失败！**", state="error", expanded=True)
            st.write("")

        else:
            st.write("")
            logger.info(f"【用户登录】 用户：{user_name} 登录成功！")
            for domain in web_setting["domain"]["domain_select"]:
                name = domains[domain]['name']
                if users[user_name]["allow_chatgpt"]:
                    if not openai_error_status:
                        if domains[domain]['type'] == "Pandora":
                            openai_url = "https://" + domain + "/auth/login_share?token=" + openai_token
                            st.link_button(f"**{name}**", openai_url, use_container_width=True)
                        elif domains[domain]['type'] == "Oaifree":
                            openai_url = get_oaifree_login_url(domain, openai_token)
                            if openai_url:
                                st.link_button(f"**{name}**", openai_url, use_container_width=True)
                                status.update(label="**用户验证成功!**", state="complete", expanded=True)
                            else:
                                st.error(f"**{name} 连接失败！**", icon=":material/error:")
                                status.update(label=f"**{name} 连接失败！**", state="error", expanded=True)

                if users[user_name]["allow_claude"]:
                    if not anthropic_error_status:
                        if domains[domain]['type'] == "Fuclaude":
                            anthropic_token = anthropic_data[user_name]["token"]
                            anthropic_url = get_fucladue_login_url(domain, anthropic_token, user_name)
                            if anthropic_url:
                                st.link_button(f"**{name}**", anthropic_url, use_container_width=True)
                                status.update(label="**用户验证成功!**", state="complete", expanded=True)
                            else:
                                st.error(f"**{name} 连接失败！**", icon=":material/error:")
                                status.update(label=f"**{name} 连接失败！**", state="error", expanded=True)
            st.write("")


# 设置页面
st.set_page_config(page_icon="LOGO.png",
                   page_title=web_setting["web"]["title"],
                   initial_sidebar_state=web_setting["web"]["sidebar_state"])

if "role" not in st.session_state:
    st.session_state.role = None
if "theme" not in st.session_state:
    st.session_state.theme = web_setting["web"]["login_theme"]


# 侧边栏
with st.sidebar:
    st.write("")
    st.write("**服务面板**")
    st.page_link("pages/uid.py", label="UID 登录", use_container_width=True, icon=":material/badge:")
    st.page_link("pages/change.py", label="密码变更", use_container_width=True, icon=":material/change_circle:")
    st.page_link("pages/refresh.py", label="账户续费", use_container_width=True, icon=":material/history:")
    st.page_link("pages/share.py", label="免费使用", use_container_width=True, icon=":material/supervisor_account:")
    st.page_link("pages/admin.py", label="管理员登录", use_container_width=True, icon=":material/account_circle:")

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
    title_html = f"""
    <div class='centered-title' style='text-align: center;'>
        <div style='font-size: 35px;'>{web_setting["web"]["title"]}</div>
    </div>
    """
    subtitle_html = f"""
    <div class='centered-subtitle' style='text-align: center;'>
        <div style='font-size: 15px;'>{web_setting["web"]["subtitle"]}</div>
    </div>
    """
    st.markdown(Simple_white_html, unsafe_allow_html=True)

    col4, col5, col6 = st.columns([0.15, 0.70, 0.15])
    with col5:
        if web_setting["web"]["notice_enable"]:
            sac.alert(label=web_setting["web"]["notice_title"], description=web_setting["web"]["notice_subtitle"], color=web_setting["web"]["notice_color"], variant=web_setting["web"]["notice_style"], banner=web_setting["web"]["notice_banner"], size=web_setting["web"]["notice_size"], radius=web_setting["web"]["notice_radius"], key="free_notice1")
    st.write("")
    st.write("")
    st.write("")
    st.markdown(title_html, unsafe_allow_html=True)
    st.markdown(subtitle_html, unsafe_allow_html=True)
    st.write("")
    col4, col5, col6 = st.columns([0.15, 0.70, 0.15])
    with col5:
        account = st.text_input("**账户**", placeholder="your account")
        password = st.text_input("**密码**", type="password", placeholder="your password")
        st.divider()
        if st.button("**登录**", use_container_width=True):
            login_result = login(account, password)
            if login_result == 0:
                st.toast('**此账户不存在或已被封禁！**', icon=':material/error:')
            elif login_result == 1:
                st.toast('**账户密码错误，请重新输入！**', icon=':material/error:')
            elif login_result == 2:
                st.session_state.role = "role"
                st.toast('**账户密码验证成功!**', icon=':material/check_circle:')
            elif login_result == 3:
                st.session_state.role = "admin"
                st.switch_page("pages/admin.py")
        if st.button("**注册**", use_container_width=True):
            select()

        try:
            if st.session_state.role == "role":
                choose(account)
        except:
            pass

        col7, col8 = st.columns([0.5, 0.5])
        with col8:
            with st.popover("More"):
                st.page_link("pages/uid.py", label="UID 登录", icon=":material/login:", use_container_width=True)
                st.page_link("pages/change.py", label="忘记密码", icon=":material/login:", use_container_width=True)
                st.page_link("pages/share.py", label="免费试用", icon=":material/login:", use_container_width=True)
                st.page_link("pages/refresh.py", label="账户续费", icon=":material/login:", use_container_width=True)

elif st.session_state.theme == "Classic Black":
    st.markdown(Classic_Black_html, unsafe_allow_html=True)
    st.markdown(f"""
        <div class='centered-title'>
            {web_setting["web"]["title"]}
        </div>
        <div class='centered-subtitle'>
            <div>{web_setting["web"]["subtitle"]}</div>
        </div>""", unsafe_allow_html=True)

    st.write("")
    col4, col5, col6 = st.columns([0.15, 0.70, 0.15])
    with col5:
        if web_setting["web"]["notice_enable"]:
            sac.alert(label=web_setting["web"]["notice_title"], description=web_setting["web"]["notice_subtitle"], banner=web_setting["web"]["notice_banner"], color=web_setting["web"]["notice_color"], variant=web_setting["web"]["notice_style"], size=web_setting["web"]["notice_size"], radius=web_setting["web"]["notice_radius"], key="free_notice")

        st.write("")
        with st.container(border=True):
            if "login" not in st.session_state:
                sac.alert(label="**欢迎，请登录！**", color="dark", variant="transparent", size="lg", radius="sm")
                user_account = st.text_input("ACCOUNT", label_visibility="collapsed", placeholder="您的账户/Enter your Account")

                if st.button("**验证账户**", use_container_width=True):
                    if user_account == web_setting["web"]["super_user"]:
                        st.session_state.login = user_account
                        st.rerun()
                    if user_account in users.keys():
                        st.session_state.login = user_account
                        st.rerun()
                    else:
                        sac.alert(label="**此账户不存在！**", color="error", variant="filled", size="sm", radius="sm", icon=True)

            else:
                sac.alert(label=f"**你好，{st.session_state.login}！**", color="success", variant="transparent", size="lg", radius="sm", icon=True)
                if st.session_state.login == web_setting["web"]["super_user"]:
                    admin_password = st.text_input("PASSWORD", type="password", label_visibility="collapsed", placeholder="管理密钥/登录密码")
                    st.write("")
                    if st.button("**继续**", use_container_width=True):
                        try:
                            sure = openai_data[st.session_state.login]["password"]
                        except:
                            sure = "Not Set"
                        if admin_password == web_setting["web"]["super_key"]:
                            st.session_state.role = "admin"
                            del st.session_state["login"]
                            st.switch_page("pages/admin.py")
                        elif sure == "Not Set":
                            sac.alert(label="**密码错误！**", color="error", variant="filled", size="sm", radius="sm", icon=True)
                        elif admin_password == users[st.session_state.login]["password"]:
                            st.session_state.role = "role"
                            login = st.session_state.login
                            token = openai_data[login]["token"]
                            group = openai_data[login]["group"]
                        else:
                            sac.alert(label="**密码错误！**", color="error", variant="filled", size="sm", radius="sm", icon=True)
                else:
                    user_password = st.text_input("PASSWORD", type="password", label_visibility="collapsed", placeholder="您的密码/Enter your Password！")
                    if st.button("**继续**", use_container_width=True):
                        if user_password == users[st.session_state.login]["password"]:
                            st.session_state.role = "role"
                        else:
                            sac.alert(label="**密码错误！**", color="error", variant="filled", size="sm", radius="sm", icon=True)

            st.write("")
            sac.divider("**OR**", align="center", key="divider", color="gray")
            st.write("")
            if st.button("**UID登录**", use_container_width=True):
                st.switch_page("pages/uid.py")
            if st.button("**加入我们**", use_container_width=True, key="select"):
                select()
            st.page_link("pages/share.py", label="**:blue[免费试用?]**")

    try:
        if st.session_state.role == "role":
            choose(st.session_state.login)
            del st.session_state["login"]
    except:
        pass

elif st.session_state.theme == "Retro Orange":
    st.markdown(Retro_Orange_html, unsafe_allow_html=True)
    st.write("")
    with st.container(border=True):
        st.markdown("""
            <div style="text-align: center; font-family: 'Times New Roman', '宋体'; font-size: 20px;">
                <p style="font-size: 20px;">Start Using ChatGPT/Claude For Free!</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("Continue With UID / UID 登录", use_container_width=True, type="secondary"):
            st.switch_page("pages/uid.py")

        st.markdown("""
            <div style="text-align: center; font-family: 'Times New Roman', '宋体'; font-size: 20px;">
                <p style="font-size: 20px;">OR</p>
            </div>
            """, unsafe_allow_html=True)

        if "login" not in st.session_state:
            user_account = st.text_input("ACCOUNT", label_visibility="collapsed", placeholder="name@yourcompany.com / 您的账户")
            st.write("")
            if st.button("Login In / 登录", use_container_width=True):
                if user_account == web_setting["web"]["super_user"]:
                    st.session_state.login = user_account
                    st.rerun()
                if user_account in users.keys():
                    st.session_state.login = user_account
                    st.rerun()
                else:
                    st.toast('**This account does not exist!**\n\n**此账户不存在！**', icon=':material/error:')

        else:
            if st.session_state.login == web_setting["web"]["super_user"]:
                if "note_success" not in st.session_state:
                    st.toast('**Success! Please enter your password!**\n\n**成功！请继续输入您的密码！**', icon=':material/error:')
                st.session_state.note_success = True
                admin_password = st.text_input("PASSWORD", type="password", label_visibility="collapsed", placeholder="Enter your Password / 填写您的密码")
                st.write("")
                if st.button("Continues / 继续", use_container_width=True):
                    try:
                        sure = openai_data[st.session_state.login]["password"]
                    except:
                        sure = "Not Set"
                    if admin_password == web_setting["web"]["super_key"]:
                        st.session_state.role = "admin"
                        del st.session_state["login"]
                        st.switch_page("pages/admin.py")
                    elif sure == "Not Set":
                        st.toast('**Password error!**\n\n**密码错误！**', icon=':material/error:')
                    elif admin_password == openai_data[st.session_state.login]["password"]:
                        st.session_state.role = "role"
                        login = st.session_state.login
                        token = openai_data[login]["token"]
                        group = openai_data[login]["group"]
                    else:
                        st.toast('**Password error!**\n\n**密码错误！**', icon=':material/error:')
            else:
                if "note_success" not in st.session_state:
                    st.toast('**Success! Please enter your password!**\n\n**成功！请继续输入您的密码！**', icon=':material/error:')
                st.session_state.note_success = True
                user_password = st.text_input("PASSWORD", type="password", label_visibility="collapsed", placeholder="Enter your Password / 填写您的密码")
                st.write("")
                if st.button("Continues / 继续", use_container_width=True):
                    if user_password == users[st.session_state.login]["password"]:
                        st.session_state.role = "role"
                    else:
                        st.toast('**Password error!**\n\n**密码错误！**', icon=':material/error:')

        if st.button("Join Us / 注册", use_container_width=True, key="select"):
            select()
        st.write("")

    try:
        if st.session_state.role == "role":
            choose(st.session_state.login)
            del st.session_state["login"]
            del st.session_state["note_success"]
    except:
        pass

    st.write("")
    st.write("")
    st.write("")
    st.markdown(f"{web_setting['web']['Retro_Orange_notice']}", unsafe_allow_html=True)  # 通知/页面

# 页脚
with open(style_path + "//footer.html", "r", encoding="utf-8") as file:
    footer_html = file.read()
    color = "white"
    if st.session_state.theme == "Retro Orange":
        color = "#efede4"
    footer_html = footer_html.replace("{{color}}", color)
st.markdown(footer_html, unsafe_allow_html=True)
st.logo("LOGO.png", link="https://github.com/Chenyme/oaifree-tools")