import os
import toml
import logging
import json
import streamlit as st
import secrets
import streamlit_antd_components as sac
from utils import get_sharetoken, get_accesstoken, get_login_url, check_sharetoken

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
with open(current_path + '/share.json', 'r', encoding='utf-8') as file:
    share_data = json.load(file)
with open(current_path + '/domain.json', 'r', encoding='utf-8') as file:
    domain_data = json.load(file)

st.set_page_config(layout="wide", page_title=web_setting["web"]["title"], page_icon="LOGO.png")

if "role" not in st.session_state:
    st.session_state.role = None

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


def check_login_status(token_result, user_name, group_result):
    error_status = False
    # 判断SA_Token是否有效
    with st.status("**正在验证您的环境...**") as status:

        if check_sharetoken(token_result):
            st.session_state.role = None
            token_result = token_result
            logger.info(f"【用户登录】 用户：{user_name} 登录成功！")
        else:
            if str(config[user_name]["expires_in"]) == "0":
                status.update(label="**SA状态已失效！尝试刷新中...**", state="running", expanded=True)
                logging.info(f"<用户> 【SA验证】 用户 {user_name} 的SA_Token已经失效！尝试刷新中...")
                sa_status, name, token_result = get_sharetoken(
                    user_name,
                    accounts[group_result]["access_token"],
                    config[user_name]["site_limit"],
                    config[user_name]["expires_in"],
                    config[user_name]["gpt35_limit"],
                    config[user_name]["gpt4_limit"],
                    config[user_name]["show_conversations"]
                )

                # 判断AC_Token是否有效
                if sa_status:
                    config[user_name]["token"] = token_result
                    config_json = json.dumps(config, indent=2)
                    with open(current_path + 'config.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(config_json)
                    logging.info(f"<用户> 【SA刷新】 用户 {user_name} 的SA_Token刷新成功！")

                else:
                    logging.info(f"<用户> 【AC刷新】 用户 {user_name} 的AC_Token已经失效！尝试刷新中...")
                    status.update(label="**AC状态已失效！尝试刷新中...**", state="running", expanded=False)
                    ac_status, user_ac_tk = get_accesstoken(accounts[group_result]["refresh_token"])

                    # 判断RF_Token是否有效
                    if ac_status:
                        status.update(label="**即将完成！请耐心等待...**", state="running", expanded=False)
                        sa_status, name, token_result = get_sharetoken(
                            user_name,
                            user_ac_tk,
                            config[user_name]["site_limit"],
                            config[user_name]["expires_in"],
                            config[user_name]["gpt35_limit"],
                            config[user_name]["gpt4_limit"],
                            config[user_name]["show_conversations"]
                        )

                        config[user_name]["token"] = token_result
                        config_json = json.dumps(config, indent=2)
                        with open(current_path + 'config.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(config_json)
                        accounts[group_result]["access_token"] = user_ac_tk
                        accounts_json = json.dumps(accounts, indent=2)
                        with open(current_path + 'accounts.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(accounts_json)
                        logging.info(f"<用户> 【AC刷新】 用户组 {group_result} 的AC_Token刷新成功！")
                    else:
                        error_status = "RF过期"
                        logging.error(
                            f"<用户> 【AC刷新】 用户组 {group_result} 的AC_Token刷新失败！请检查RF_Token是否正确！")
            else:
                error_status = "过期"
                logging.error(f"<用户> 【SA验证】 用户 {user_name} 的SA_Token已经过期！")

        status.update(label="**环境验证成功！**", state="complete", expanded=False)
    return error_status, token_result


@st.experimental_dialog("成为我们的新伙伴！")  # 注册模块
def select():
    st.write("")
    st.write("")
    user_new_acc = st.text_input("**账户：**", placeholder="您的账户")
    user_new_pass = st.text_input("**密码：**", type="password", placeholder="您的密码")
    user_new_invite = st.text_input("**邀请令牌：**", placeholder="您的邀请令牌，输入后请Enter确认！")
    uid = "UID-" + secrets.token_urlsafe(32)
    st.divider()
    st.write("")
    if web_setting["web"]["invite_link_enable"]:
        st.link_button("**获取令牌**", web_setting["web"]["invite_link"], use_container_width=True)

    if st.button("**加入我们**", use_container_width=True, type="primary"):
        st.write("")
        if user_new_acc == "":
            st.error("请填写您的账户!", icon=":material/error:")
        elif user_new_pass == "":
            st.error("请填写您的密码!", icon=":material/error:")
        elif user_new_acc in config:
            st.error("该账户已存在!", icon=":material/error:")
        elif user_new_invite not in invite_config.keys():
            st.error("无效的邀请令牌！", icon=":material/error:")
        elif not invite_config[user_new_invite]['used']:
            user_new_group = invite_config[user_new_invite]['group']
            group_data = accounts[user_new_group]
            acc = group_data['access_token']
            status, new_name, new_token_key = get_sharetoken(user_new_acc, acc, web_setting["web"]["site_limit"], web_setting["web"]["expires_in"], web_setting["web"]["gpt35_limit"], web_setting["web"]["gpt4_limit"], web_setting["web"]["show_conversations"])

            if status:

                json_data = {
                    new_name: {
                        'password': user_new_pass,
                        'token': new_token_key,
                        'uid': uid,
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
                config_json = json.dumps(config, indent=2)

                invite_config[user_new_invite]['used'] = True
                with open(current_path + '/invite.json', 'w') as file:
                    json.dump(invite_config, file, indent=2)

                with open(current_path + 'config.json', 'w', encoding='utf-8') as json_file:
                    json_file.write(config_json)

                logger.info(f"name：{new_name}，token:{new_token_key}，group:{user_new_group}，注册邀请码：{user_new_invite}")
                logger.info(f"【用户注册】 新用户：{new_name} 注册成功！")
                sac.alert(label="**恭喜，注册成功！**",
                          description=f"您的专属 **UID** （可用于密码更改、用户登录）：**{uid}** ", color="success",
                          variant="filled", size="md", radius="md", icon=True, closable=True)
                sac.alert(label=f"**请务必牢记并保存您的UID！**", color="success", banner=True, variant="filled",
                          size="md", radius="md", icon=True, closable=True)
            else:
                sac.alert(label="**注册失败，请联系管理员！**", color="error", variant="filled", size="md", radius="md", icon=True, closable=True)
        else:
            st.error("邀请令牌已被使用！请更换令牌", icon=":material/error:")

    st.write("")


@st.experimental_dialog("身份验证")  # 选择模块
def choose(user_name, login_result, token_result, group_result):
    st.write(f"## 欢迎您，{user_name}！")
    st.write("")
    st.write("")

    if web_setting["web"]["choose_domain"] == "不允许":
        error_status, token_result = check_login_status(token_result, user_name, group_result)

        with st.status("**正在验证您的身份...**") as status:
            if error_status == "RF过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**验证失败，请联系管理员！**", color="error", variant="filled", size="md", radius="md", icon=True, closable=True)
            elif error_status == "过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**账户已过期，请联系管理员续费！**", color="error", variant="filled", size="md", radius="md", icon=True, closable=True)
            else:
                status.update(label="**即将验证完毕...感谢您的等待！**", state="running", expanded=False)
                domain = web_setting["web"]["domain"]

                if domain_data[domain]['type'] == "Classic":  # 判断服务站类型
                    url = "https://" + domain + "/auth/login_share?token=" + token_result
                else:
                    url = get_login_url(domain, token_result)

                st.write("")
                st.link_button("**开始使用**", url, use_container_width=True)
                status.update(label="**用户验证成功!**", state="complete", expanded=True)

    else:
        error_status, token_result = check_login_status(token_result, user_name, group_result)

        with st.status("**正在验证您的身份...**") as status:
            if error_status == "RF过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**验证失败，请联系管理员！**", color="error", variant="filled", size="md", radius="md", icon=True, closable=True)
            elif error_status == "过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**账户已过期，请联系管理员续费！**", color="error", variant="filled", size="md", radius="md", icon=True, closable=True)
            else:
                status.update(label="**即将验证完毕...感谢您的等待！**", state="running", expanded=False)
                st.write("")
                for domain in web_setting["web"]["user_domain"]:
                    if domain_data[domain]['type'] == "Classic":  # 判断服务站类型
                        url = "https://" + domain + "/auth/login_share?token=" + token_result
                    else:
                        url = get_login_url(domain, token_result)
                    st.write("")
                    name = domain_data[domain]['name']
                    st.link_button(f"**{name}**", url, use_container_width=True)
                status.update(label="**用户验证成功!**", state="complete", expanded=True)


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
    account = st.text_input("**账户**", placeholder="account")
    password = st.text_input("**密码**", type="password", placeholder="password")
    st.write("---")
    if st.button("**登录**", use_container_width=True):
        login_result, token_result, group_result = login(account, password)
        if login_result == 0:
            st.toast('**此账户不存在或已被封禁！**', icon=':material/error:')
        elif login_result == 1:
            st.toast('**账户密码错误，请重新输入！**', icon=':material/error:')
        elif login_result == 2:
            st.session_state.role = "role"
            st.toast('账户密码验证成功!', icon=':material/check_circle:')
        elif login_result == 3:
            st.session_state.role = "admin"
            logger.info(f"【管理登录】 管理员：{account} 登录成功！")
            st.switch_page("pages/admin.py")

    if st.button("**注册**", use_container_width=True):
        select()

    try:
        if st.session_state.role == "role":
            choose(account, login_result, token_result, group_result)
    except:
        pass

    st.write("")
    st.page_link("pages/refresh.py", label=":red[**忘记密码？账户过期？**]", icon=":material/login:", use_container_width=True)
    st.page_link("pages/share.py", label="**Share共享站**", icon=":material/login:", use_container_width=True)

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
