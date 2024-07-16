import streamlit as st
import requests
import toml
import json
import secrets
import os
from utils import get_sharetoken, get_accesstoken, get_oaifree_login_url, get_fucladue_login_url, check_sharetoken
import logging
import base64

path = os.path.abspath('.')
style_path = path + '/style/'
current_path = path + '/config/'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(current_path + "/app.log", encoding='utf-8'),
                              logging.StreamHandler()])
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
with open(style_path + "//Classic_Black.html", "r", encoding="utf-8") as file:  # 网页样式
    Classic_Black_html = file.read()
with open(style_path + "//Retro_Orange.html", "r", encoding="utf-8") as file:  # 网页样式
    Retro_Orange_html = file.read()
    Retro_Orange_html = Retro_Orange_html.replace("""</style>
<body>
    <div class="typewriter">
        <h1>{{text}}</h1>
    </div>
</body>
<body>
    <div class="responsive-text">
        <p>with <strong>OiaT</strong></p>
    </div>
</body>
<style>""", "")
with open(style_path + "//sidebar.html", "r", encoding="utf-8") as file:  # 网页样式
    sidebar_html = file.read()
with open(current_path + 'secret.toml', 'r') as f:
    secret_setting = toml.load(f)
    CLIENT_ID = secret_setting['linux_do']['CLIENT_ID']
    CLIENT_SECRET = secret_setting['linux_do']['CLIENT_SECRET']
    REDIRECT_URI = secret_setting['linux_do']['REDIRECT_URI']
    AUTHORIZATION_ENDPOINT = secret_setting['linux_do']['AUTHORIZATION_ENDPOINT']
    TOKEN_ENDPOINT = secret_setting['linux_do']['TOKEN_ENDPOINT']
    USER_ENDPOINT = secret_setting['linux_do']['USER_ENDPOINT']


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


st.set_page_config(page_title=web_setting["web"]["title"], page_icon=style_path + "logo.png")

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

try:
    code = st.query_params["code"]
    state = st.query_params["state"]
    if state != st.secrets["secret_key"]:
        st.error("""
        **401：State value does not match!**

        **状态值不匹配，请尝试重新验证！**
        """, icon=":material/error:")
        st.stop()

    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Accept': 'application/json'}
    response = requests.post(TOKEN_ENDPOINT, auth=auth, data=data, headers=headers)

    if response.status_code == 200:
        user_response = requests.get(USER_ENDPOINT,
                                     headers={'Authorization': 'Bearer ' + response.json()['access_token']})
        if user_response.status_code == 200:
            user_linux_do_data = user_response.json()
        else:
            st.error(str(user_response.status_code) + '：**Failed to fetch user info!**', icon=":material/error:")
            st.stop()
    else:
        st.error(str(response.status_code) + '：**Failed to fetch access token!**', icon=":material/error:")
        st.stop()

    logger.info(f"【LinuxDo】 LinuxDo用户：{user_linux_do_data['username']} 登录成功")
    with open(style_path + '/Linux_do.webp', "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    if str(user_linux_do_data["username"]) + "@linux.do" not in users.keys():
        name = str(user_linux_do_data["username"]) + "@linux.do"
        password = str(user_linux_do_data["username"])
        uid = "UID-" + secrets.token_urlsafe(32)
        note = f"LinuxDo {user_linux_do_data['trust_level']}级用户"
        with st.container(border=True):
            col1, col2, col3 = st.columns([0.78, 0.19, 0.03])
            with col1:
                st.markdown(f"""
                <div class="image-container">
                    <img src="data:image/png;base64,{encoded_image}" alt="Encoded Image" style="width: 40%; margin-top: 0px;">
                </div>
                <style>
                .welcome-message {{
                    font-size: 24px;
                    color: #4CAF50;
                    font-weight: bold;
                    text-align: center;
                    margin-top: 0px;
                }}
                .uid-message {{
                    font-size: 18px;
                    color: #444;
                    text-align: center;
                    margin-bottom: 15px;
                    font-weight: bold;
                }}
                @media screen and (max-width: 640px) {{
                    .welcome-message {{
                        font-size: 19px;
                        margin-top: 5px;
                    }}
                    .uid-message {{
                        font-size: 12px;
                        margin-bottom: 20px;
                        margin-top: -15px;
                    }}
                    .image-container2 {{
                        position: relative;
                        text-align: right;
                        width: 20%;
                        margin-top: -70px;
                    }}
                }}
                </style>
                <div class="welcome-message">欢迎使用 LINUX DO 登录</div>
                """, unsafe_allow_html=True)
                st.write("")
                with col2:
                    try:
                        st.markdown(f"""                
                        <div class="image-container2" style="float: right;">
                            <img src="{user_linux_do_data["avatar_url"]}" alt="Image" style="width: 100%; margin-top: 100px;">
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        st.markdown(f"""                
                        <div class="image-container2" style="float: right;">
                            <img src="{user_linux_do_data["avatar_template"]}" alt="Image" style="width: 100%; margin-top: 100px;">
                        </div>
                          """, unsafe_allow_html=True)
                with st.spinner("**系统正在创建账户...请耐心等待！**"):
                    if int(user_linux_do_data['trust_level']) == 1:
                        level = "linux_do_1"
                    elif int(user_linux_do_data['trust_level']) == 2:
                        level = "linux_do_2"
                    elif int(user_linux_do_data['trust_level']) == 3:
                        level = "linux_do_3"
                    elif int(user_linux_do_data['trust_level']) == 4:
                        level = "linux_do_4"
                    else:
                        level = None
                    allow_chatgpt = secret_setting[level]["chatgpt"]
                    allow_claude = secret_setting[level]["claude"]
                    chatgpt_group = secret_setting[level]["chatgpt_group"]
                    claude_group = secret_setting[level]["claude_group"]
                    site_limit = secret_setting[level]["site_limit"]
                    expires_in = secret_setting[level]["expires_in"]
                    gpt35_limit = secret_setting[level]["gpt35_limit"]
                    gpt4_limit = secret_setting[level]["gpt4_limit"]
                    show_conversations = secret_setting[level]["show_conversations"]

                    if allow_chatgpt:
                        ac_token = accounts[chatgpt_group]['access_token']
                        status, new_name, new_token_key = get_sharetoken(name, ac_token, site_limit, expires_in, gpt35_limit, gpt4_limit, show_conversations)
                        if status:
                            st.session_state.signup1 = True
                            json_data_2 = {
                                name: {
                                    'token': new_token_key,
                                    'group': chatgpt_group,
                                    'type': accounts[chatgpt_group]['account_type'],
                                    'site_limit': site_limit,
                                    'expires_in': expires_in,
                                    'gpt35_limit': gpt35_limit,
                                    'gpt4_limit': gpt4_limit,
                                    'show_conversations': show_conversations,
                                }
                            }
                            openai_data.update(json_data_2)
                            openai_datas = json.dumps(openai_data, indent=2)
                            with open(current_path + 'openai.json', 'w', encoding='utf-8') as json_file:
                                json_file.write(openai_datas)
                        elif not allow_chatgpt:
                            for user in openai_data.keys():
                                if user == name:
                                    del openai_data[user]
                        else:
                            logger.error(f"【LinuxDo】 尝试创建LinuxDO用户失败，请管理员检查 的 AC_Token 状态！")
                            st.error(f"**尝试用户创建失败，请联系管理员检查 的 AC_Token 状态！**", icon=":material/error:")
                            st.write("")
                    else:
                        st.session_state.signup1 = True

                    if allow_claude and "signup1" in st.session_state:
                        json_data_3 = {
                            name: {
                                'token': accounts[claude_group]['access_token'],
                                'group': claude_group,
                                'type': accounts[claude_group]['account_type']
                            }
                        }
                        anthropic_data.update(json_data_3)
                        anthropic_datas = json.dumps(anthropic_data, indent=2)
                        with open(current_path + 'anthropic.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(anthropic_datas)
                    elif not allow_claude:
                        for user in anthropic_data.keys():
                            if user == name:
                                del anthropic_data[user]
                    if "signup1" in st.session_state:
                        json_data_1 = {
                            name: {
                                'password': password,
                                'uid': uid,
                                'allow_chatgpt': allow_chatgpt,
                                'allow_claude': allow_claude,
                                'note': note,
                            }
                        }
                        users.update(json_data_1)
                        user_datas = json.dumps(users, indent=2)
                        with open(current_path + 'users.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(user_datas)
                        logging.info(f"【LinuxDo】 LinuxDo用户创建成功：{name}")
                        st.toast("**用户创建成功！**", icon=":material/check_circle:")
                    else:
                        st.error(f"**尝试用户创建失败，请联系管理员！**", icon=":material/error:")
                        st.write("")
                        st.stop()
                st.markdown(f"""
                <div class="uid-message">账户：{user_linux_do_data["username"] + '@linux.do'}</div>
                <div class="uid-message">密码：{user_linux_do_data["username"] + '-' + secrets.token_urlsafe(5)}</div>
                <div class="uid-message">{uid}</div>
                """, unsafe_allow_html=True)
                st.toast("**请及时前往首页修改您的密码！**", icon=":material/check_circle:")
                st.session_state.linux_do = True
                user_name = name
    else:
        with st.container(border=True):
            col1, col2, col3 = st.columns([0.78, 0.19, 0.03])
            with col1:
                st.toast("**Login In Success By Linux.DO!** \n\n **Linux.DO 登录成功！**",
                         icon=":material/check_circle:")
                user_name = str(user_linux_do_data["username"]) + "@linux.do"
                st.markdown(f"""
                <div class="image-container">
                    <img src="data:image/png;base64,{encoded_image}" alt="Encoded Image" style="width: 40%; margin-top: 0px;">
                </div>
                <style>
                .welcome-message {{
                    font-size: 24px;
                    color: #4CAF50;
                    font-weight: bold;
                    text-align: center;
                    margin-top: 0px;
                }}
                .uid-message {{
                    font-size: 18px;
                    color: #444;
                    text-align: center;
                    margin-bottom: 15px;
                    font-weight: bold;
                }}
                @media screen and (max-width: 640px) {{
                    .welcome-message {{
                        font-size: 19px;
                        margin-top: 5px;
                    }}
                    .uid-message {{
                        font-size: 12px;
                        margin-bottom: 20px;
                        margin-top: -15px;
                    }}
                    .image-container2 {{
                        position: relative;
                        text-align: right;
                        width: 20%;
                        margin-top: -70px;
                    }}
                }}
                </style>
                <div class="welcome-message">欢迎！{user_name}</div>
                <br>
                <div class="uid-message">请牢记您的UID：</div>
                <div class="uid-message">{users[user_name]['uid']}</div>
                """, unsafe_allow_html=True)
                st.write("")
            with col2:
                try:
                    st.markdown(f"""                
                    <div class="image-container2" style="float: right;">
                        <img src="{user_linux_do_data["avatar_url"]}" alt="Image" style="width: 100%; margin-top: 80px;">
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    st.markdown(f"""                
                    <div class="image-container2" style="float: right;">
                        <img src="{user_linux_do_data["avatar_template"]}" alt="Image" style="width: 100%; margin-top: 80px;">
                    </div>
                      """, unsafe_allow_html=True)
            st.session_state.linux_do = True

    if "linux_do" in st.session_state:
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
                    col1, col2, col3 = st.columns([0.18, 0.64, 0.18])
                    with col2:
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
                col1, col2, col3 = st.columns([0.18, 0.64, 0.18])
                with col2:
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
except:
    st.error("""
    **401：Unauthorized!**
    
    **未授权访问！**
    """, icon=":material/error:")
st.write("")
st.write("")
st.write("")
st.markdown(f"{web_setting['web']['Retro_Orange_notice']}", unsafe_allow_html=True)  # 通知/页面