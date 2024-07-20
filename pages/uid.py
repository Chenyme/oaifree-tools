import os
import json
import toml
import base64
import logging
import streamlit as st
import streamlit_antd_components as sac
from utils import get_oaifree_login_url, get_sharetoken, check_sharetoken, get_accesstoken, get_fucladue_login_url

style_path = os.path.abspath('.') + '/style/'
current_path = os.path.abspath('.') + '/config/'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(current_path + "app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

version = "v1.2.1"

# 读取配置文件
def read_config():
    with open(current_path + '/secret.toml', 'r', encoding='utf-8') as file:  # 新增设置
        secret_setting = toml.load(file)
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
    with open(style_path + "//Classic_Black.html", "r", encoding="utf-8") as file:  # 网页样式
        Classic_Black_html = file.read()
    with open(style_path + "//Retro_Orange.html", "r", encoding="utf-8") as file:  # 网页样式
        Retro_Orange_html = file.read()
        Retro_Orange_html = Retro_Orange_html.replace("{{text}}", "Deepen understanding")
    with open(style_path + "//sidebar.html", "r", encoding="utf-8") as file:  # 网页样式
        sidebar_html = file.read()
    with open("LOGO.png", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    st.session_state.web_setting = web_setting
    st.session_state.secret_setting = secret_setting
    st.session_state.users = users
    st.session_state.accounts = accounts
    st.session_state.domains = domains
    st.session_state.openai_data = openai_data
    st.session_state.anthropic_data = anthropic_data
    st.session_state.invite_config = invite_config
    st.session_state.Simple_white_html = Simple_white_html
    st.session_state.Classic_Black_html = Classic_Black_html
    st.session_state.Retro_Orange_html = Retro_Orange_html
    st.session_state.sidebar_html = sidebar_html
    st.session_state.encoded_image = encoded_image


if "web_setting" not in st.session_state:
    read_config()

web_setting = st.session_state.web_setting
secret_setting = st.session_state.secret_setting
users = st.session_state.users
accounts = st.session_state.accounts
domains = st.session_state.domains
openai_data = st.session_state.openai_data
anthropic_data = st.session_state.anthropic_data
invite_config = st.session_state.invite_config
Simple_white_html = st.session_state.Simple_white_html
Classic_Black_html = st.session_state.Classic_Black_html
Retro_Orange_html = st.session_state.Retro_Orange_html
sidebar_html = st.session_state.sidebar_html
encoded_image = st.session_state.encoded_image
Retro_Orange_html = Retro_Orange_html.replace("{{text}}", "Brainstorm your ideas")

if "theme" not in st.session_state:
    st.session_state.theme = web_setting["web"]["login_theme"]


@st.experimental_dialog("什么是UID？")
def read():
    html_content = """
    <style>
        .info-container {
            position: relative;
            padding: 20px;
            border-radius: 15px;
        }
        .info-title {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            color: #333;
        }
        .info-text {
            font-size: 18px;
            line-height: 1.6;
            color: #555;
        }
        .important {
            color: #d9534f;
            font-weight: bold;
        }
        .background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: -1;
        }
        .ball {
            position: absolute;
            border-radius: 50%;
            animation: bounce 10s infinite ease-in-out;
            opacity: 0.7;
        }
        .ball:nth-child(1) {
            width: 60px;
            height: 60px;
            background-color: rgba(255, 99, 71, 0.6);
            top: 10%;
            left: 15%;
        }
        .ball:nth-child(2) {
            width: 40px;
            height: 40px;
            background-color: rgba(30, 144, 255, 0.6);
            top: 20%;
            left: 25%;
            animation-delay: 2s;
        }
        .ball:nth-child(3) {
            width: 50px;
            height: 50px;
            background-color: rgba(34, 139, 34, 0.6);
            top: 30%;
            left: 35%;
            animation-delay: 4s;
        }
        .ball:nth-child(4) {
            width: 70px;
            height: 70px;
            background-color: rgba(255, 215, 0, 0.6);
            top: 40%;
            left: 45%;
            animation-delay: 6s;
        }
        .ball:nth-child(5) {
            width: 30px;
            height: 30px;
            background-color: rgba(138, 43, 226, 0.6);
            top: 50%;
            left: 55%;
            animation-delay: 8s;
        }
        .ball:nth-child(6) {
            width: 80px;
            height: 80px;
            background-color: rgba(75, 0, 130, 0.6);
            top: 60%;
            left: 65%;
            animation-delay: 10s;
        }
        @keyframes bounce {
            0% {
                transform: translate(0, 0) scale(1);
            }
            25% {
                transform: translate(50px, -50px) scale(1.2);
            }
            50% {
                transform: translate(-50px, 50px) scale(0.8);
            }
            75% {
                transform: translate(50px, 50px) scale(1.2);
            }
            100% {
                transform: translate(0, 0) scale(1);
            }
        }
    </style>

    <div class="background">
        <div class="ball"></div>
        <div class="ball"></div>
        <div class="ball"></div>
        <div class="ball"></div>
        <div class="ball"></div>
        <div class="ball"></div>
    </div>

    <div class="info-container">
        <p class="info-text">UID 是您的唯一标识符，用于识别您的账户。</p>
        <p class="info-text">它是在您<strong>注册时自动生成的</strong>，唯一且重要。</p>
        <p class="info-text">当您登录时，验证系统会显示您的 UID，请牢记。</p>
        <p class="info-text">UID 可用于<strong>直接登录</strong>，也可以用于<strong>找回密码</strong>。</p>
        <p class="info-text">如果您忘记了您的 UID，可以联系管理员获取。</p>
        <p class="info-text important">请妥善保管您的 UID，不要随意泄露给他人。</p>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


def find_user_details_by_uid(uid):
    user_name = None
    for key, value in users.items():
        if value["uid"] == uid:
            user_name = key
            break
    return user_name


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
                    logger.info(f"【用户登录】 用户：{user_name} 的 SA 已过期！")
                    status.update(label="**SA状态已失效！尝试刷新中...**", state="running", expanded=True)
                    sa_status, name, token_result = get_sharetoken(
                        user_name,
                        accounts[group_result]["access_token"],
                        openai_data[user_name]["site_limit"],
                        openai_data[user_name]["expires_in"],
                        openai_data[user_name]["gpt35_limit"],
                        openai_data[user_name]["gpt4_limit"],
                        openai_data[user_name]["show_conversations"])

                    if sa_status:
                        logger.info(f"【用户登录】 用户：{user_name} 的 SA 刷新成功！")
                        openai_data[user_name]["token"] = token_result
                        config_json = json.dumps(openai_data, indent=2)
                        with open(current_path + 'openai.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(config_json)
                    else:
                        logger.info(f"【用户登录】 用户组：{group_result} 的 SA 刷新失败！")
                        status.update(label="**AC状态已失效！尝试刷新中...**", state="running", expanded=False)
                        ac_status, user_ac_token = get_accesstoken(accounts[group_result]["refresh_token"])
                        if ac_status:
                            logger.info(f"【用户登录】 用户组：{group_result} 的 AC 刷新成功！")
                            status.update(label="**即将完成！请耐心等待...**", state="running", expanded=False)
                            sa_status, name, token_result = get_sharetoken(
                                user_name,
                                user_ac_token,
                                openai_data[user_name]["site_limit"],
                                openai_data[user_name]["expires_in"],
                                openai_data[user_name]["gpt35_limit"],
                                openai_data[user_name]["gpt4_limit"],
                                openai_data[user_name]["show_conversations"])

                            openai_data[user_name]["token"] = token_result
                            config_json = json.dumps(openai_data, indent=2)
                            accounts[group_result]["access_token"] = user_ac_token
                            accounts_json = json.dumps(accounts, indent=2)
                            with open(current_path + 'openai.json', 'w', encoding='utf-8') as json_file:
                                json_file.write(config_json)
                            with open(current_path + 'accounts.json', 'w', encoding='utf-8') as json_file:
                                json_file.write(accounts_json)
                        else:
                            logger.info(f"【用户登录】 用户组：{group_result} 的 AC 刷新失败！")
                            error_status = "RF过期"
                else:
                    error_status = "过期"
            else:
                error_status = "SA过期"
        status.update(label="**环境验证成功！**", state="complete", expanded=False)
    return error_status, token_result


def check_anthropic(token_result, user_name):  # 看看始皇后续有没有大动作啦!
    return False, False


@st.experimental_dialog("UID 验证")
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
                                st.link_button(f"**{name}**", f"https://{domain}{anthropic_url}", use_container_width=True)
                                status.update(label="**用户验证成功!**", state="complete", expanded=True)
                            else:
                                st.error(f"**{name} 连接失败！**", icon=":material/error:")
                                status.update(label=f"**{name} 连接失败！**", state="error", expanded=True)
            st.write("")


st.set_page_config(page_icon="LOGO.png",
                   page_title=web_setting["web"]["title"],
                   initial_sidebar_state=web_setting["web"]["sidebar_state"])

# 侧边栏
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
    col4, col5, col6 = st.columns([0.15, 0.7, 0.15])
    with col5:
        st.write("")
        st.write("")
        st.write("")
        uid = st.text_input("**UID**", key="uid", placeholder="Enter your UID", type="password")
        st.write("")
        st.write("")
        st.write("")
        if st.button("**验证 UID**", use_container_width=True):
            if uid:
                user_name= find_user_details_by_uid(uid)
                if user_name is not None:
                    st.session_state.role = "role"
                else:
                    st.toast("**UID不存在 !**", icon=":material/error:")
            else:
                st.toast("**UID不能为空！**", icon=":material/error:")
        if st.button("**没有 UID?**", use_container_width=True):
            read()
        if st.button("**返回首页**", use_container_width=True):
            st.switch_page("home.py")
    try:
        if st.session_state.role == "role":
            choose(user_name)
    except:
        pass

elif st.session_state.theme == "Classic Black":
    st.markdown(Classic_Black_html, unsafe_allow_html=True)
    st.markdown(f"<div class='centered-title'><h1>" + web_setting["web"]["title"] + "</h1></div><div class='centered-subtitle'><div>" + web_setting["web"]["subtitle"] + "</div></div>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    st.write("")
    col4, col5, col6 = st.columns([0.15, 0.7, 0.15])
    with col5:
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
            st.write("**UID**")
            uid = st.text_input("请输入UID", key="uid", placeholder="你的UID/Enter your UID", type="password", label_visibility="collapsed")
            if st.button("**验证UID**", use_container_width=True):
                if uid:
                    user_name = find_user_details_by_uid(uid)
                    if user_name is not None:
                        st.session_state.role = "role"
                    else:
                        sac.alert(label="**未查询到相关UID！**", color="error", variant="filled", size="sm", radius="sm", icon=True)
                else:
                    sac.alert(label="**UID不能为空！**", color="error", variant="filled", size="sm", radius="sm", icon=True)
            st.write("")
            sac.divider("**OR**", align="center", color="gray")
            st.write("")
            if st.button("**我没有UID?**", use_container_width=True):
                read()
            if st.button("**返回首页**", use_container_width=True):
                st.switch_page("home.py")
            st.write("")

    try:
        if st.session_state.role == "role":
            choose(user_name)
    except:
        pass

elif st.session_state.theme == "Retro Orange":
    st.markdown(Retro_Orange_html, unsafe_allow_html=True)
    st.write("")
    col1, col2, col3 = st.columns([0.12, 0.76, 0.12])
    with col2:
        with st.container(border=True):
            st.markdown("""<div style="text-align: center; font-family: 'Times New Roman', '宋体'; font-size: 20px;"><p style="font-size: 20px;">Start Using ChatGPT/Claude For Free!</p></div>""", unsafe_allow_html=True)
            if st.button("Continue With Account / 用账户登录", use_container_width=True):
                st.switch_page("home.py")
            st.markdown("""<div style="text-align: center; font-family: 'Times New Roman', '宋体'; font-size: 20px;"><p style="font-size: 20px;">OR</p></div>""", unsafe_allow_html=True)
            uid = st.text_input("请输入UID", key="uid", placeholder="Enter your UID / 填写您的UID", type="password", label_visibility="collapsed")
            st.write("")
            if st.button("Verify Your UID / 验证", use_container_width=True):
                if uid:
                    user_name = find_user_details_by_uid(uid)
                    if user_name is not None:
                        st.session_state.role = "role"
                        choose(user_name)
                    else:
                        st.toast("**Invalid UID!** \n\n **无效的UID，请重新填写！**", icon=":material/error:")
                else:
                    st.toast("**UID must not be empty！** \n\n **UID不能为空，请填写再尝试！**", icon=":material/error:")
            if st.button("I Don't Have UID? / 我没有 UID ？", use_container_width=True):
                read()
            st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.markdown(f"{web_setting['web']['Retro_Orange_notice']}", unsafe_allow_html=True)  # 通知/页面

with open(style_path + "//footer.html", "r", encoding="utf-8") as file:
    footer_html = file.read()
    color = "white"
    if st.session_state.theme == "Retro Orange":
        color = "#efede4"
    footer_html = footer_html.replace("{{color}}", color)
st.markdown(footer_html, unsafe_allow_html=True)
st.logo("LOGO.png", link="https://github.com/Chenyme/oaifree-tools")
