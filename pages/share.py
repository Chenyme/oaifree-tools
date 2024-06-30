import os
import json
import toml
import logging
import streamlit as st
import streamlit_antd_components as sac
from utils import get_login_url, get_sharetoken, check_sharetoken, get_accesstoken

current_path = os.path.abspath('.') + '/config/'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(current_path + "app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    web_setting = toml.load(file)
with open(current_path + '/share.json', 'r', encoding='utf-8') as file:
    share_data = json.load(file)
with open(current_path + '/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    accounts = json.load(file)
with open(current_path + '/domain.json', 'r', encoding='utf-8') as file:
    domain_data = json.load(file)

st.set_page_config(page_title=web_setting["web"]["title"], page_icon="LOGO.png")

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
    error = False

    # 判断SA_Token是否有效
    if check_sharetoken(token_result):

        token_result = token_result
        logging.info(f"<用户> 【用户登录】 用户：{user_name} 登录成功！")
    else:
        if str(config[user_name]["expires_in"]) == "0":
            logging.info(f"<用户> 【SA验证】 用户 {user_name} 的SA_Token已经失效！尝试刷新中...")
            status.update(label="**账户SA状态已失效！尝试刷新中...**", state="running", expanded=False)
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
                status.update(label="**账户AC状态已失效！尝试刷新中...**", state="running", expanded=False)
                ac_status, user_ac_tk = get_accesstoken(accounts[group_result]["refresh_token"])

                # 判断RF_Token是否有效
                if ac_status:
                    status.update(label="**已成功刷新！请耐心等待...**", state="running", expanded=False)
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
                    error = "RF过期"
                    logging.error(
                        f"<用户> 【AC刷新】 用户组 {group_result} 的AC_Token刷新失败！请检查RF_Token是否正确！")
        else:
            error = "过期"
            logging.error(f"<用户> 【SA验证】 用户 {user_name} 的SA_Token已经过期！")

    return error, token_result


@st.experimental_dialog("身份验证")  # 选择模块
def choose(user_name, login_result, token_result, group_result):
    st.write(f"## 欢迎您，{user_name}！")
    st.write("")
    st.write("")

    if web_setting["web"]["choose_domain"] == "不允许":
        with st.status("**正在验证您的身份...**") as status:
            error, token_result = check_login_status(token_result, user_name, group_result)
            if error == "RF过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**验证失败，请联系管理员！**", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
            elif error == "过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**账户已过期，请联系管理员续费！**", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
            else:
                status.update(label="**即将验证完毕...感谢您的等待！**", state="running", expanded=False)
                domain = web_setting["web"]["domain"]

                if domain_data[domain]['type'] == "Classic":  # 判断服务站类型
                    url = "https://" + domain + "/auth/login_share?token=" + token_result
                else:
                    url = get_login_url(domain, token_result)

                st.write("")
                st.link_button("**开始使用**", url, use_container_width=True)
                status.update(label="**验证成功!**", state="complete", expanded=True)

    else:
        with st.status("**正在验证您的身份...**") as status:
            error, token_result = check_login_status(token_result, user_name, group_result)
            if error == "RF过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**验证失败，请联系管理员！**", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
            elif error == "过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**账户已过期，请联系管理员续费！**", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
            else:
                status.update(label="**即将验证完毕...请稍后！**", state="running", expanded=False)
                st.write("")
                for domain in web_setting["web"]["user_domain"]:
                    if domain_data[domain]['type'] == "Classic":  # 判断服务站类型
                        url = "https://" + domain + "/auth/login_share?token=" + token_result
                    else:
                        url = get_login_url(domain, token_result)
                    st.write("")
                    name = domain_data[domain]['name']
                    st.link_button(f"**{name}**", url, use_container_width=True)
                status.update(label="**验证成功!**", state="complete", expanded=True)


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
    """, unsafe_allow_html=True)  # 按钮样式

st.markdown("<div style='text-align:center;'><h1 style='text-align:center;'>" + web_setting["web"]["title"] + "</h1></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'><div>" + web_setting["web"]["subtitle"] + "</div></div>", unsafe_allow_html=True)

st.title("")
sac.alert(label=web_setting["web"]["share_notice"], color=web_setting["web"]["notice_color"],
                      variant=web_setting["web"]["notice_style"], banner=web_setting["web"]["notice_banner"], size=web_setting["web"]["notice_size"], radius=web_setting["web"]["notice_radius"], icon=True, closable=True)

st.divider()
if web_setting["web"]["share"]:

    st.write("")
    key = st.selectbox("**选择要登录的Share账户**", list(share_data.keys()), index=0)
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("**点我登录**", use_container_width=True, key="login1"):
            st.session_state.role = "role"
        try:
            if st.session_state.role == "role":
                choose(key, True, share_data[key]['token'], share_data[key]['group'])
                st.session_state.role = None
        except:
            pass

    with col2:
        if st.button("**返回首页**", use_container_width=True):
            st.switch_page("home.py")
    st.write("")
    st.write("")
    i = 1
    col1, col2 = st.columns(2)
    for key in share_data.keys():
        if i % 2 == 1:
            with col1:
                with st.expander("**共享账户** " + str(i), expanded=True, icon=":material/apps:"):
                    st.write("")
                    if share_data[key]['type'] == "Free":
                        sac.tags([sac.Tag("GPT-3.5", color="green")], size="md", key=i)
                        st.write("账户昵称：**" + key + "**")
                    elif share_data[key]['type'] == "Plus":
                        sac.tags([sac.Tag("GPT-3.5", color="green"), sac.Tag("GPT-4", color="blue"), sac.Tag("GPT-4o", color="red")], size="md", key=i)
                        st.write("账户昵称：**" + key + "**")
                        if str(share_data[key]['gpt4_limit']) == "-1":
                            st.write("GPT4 次数：**无限制**")
                        else:
                            st.write("GPT4 次数：**限制 - " + str(share_data[key]['gpt4_limit']) + "次**")

                    if str(share_data[key]['gpt35_limit']) == "-1":
                        st.write("GPT3.5 次数：**无限制**")
                    else:
                        st.write("GPT3.5 次数：**限制 - " + str(share_data[key]['gpt35_limit']) + "次**")

                    if str(share_data[key]['expires_in']) == "0":
                        st.write("账户到期时间：**永不过期**")
                    else:
                        st.write("账户到期时间：**" + str(share_data[key]['expires_in']) + "**")
                    st.write("")
        if i % 2 == 0:
            with col2:
                with st.expander("**共享账户** " + str(i), expanded=True, icon=":material/apps:"):
                    st.write("")
                    if share_data[key]['type'] == "Free":
                        sac.tags([sac.Tag("GPT-3.5", color="green")], size="md", key=i)
                        st.write("账户昵称：**" + key + "**")
                    elif share_data[key]['type'] == "Plus":
                        sac.tags([sac.Tag("GPT-3.5", color="green"), sac.Tag("GPT-4", color="blue"), sac.Tag("GPT-4o", color="red")], size="md", key=i)
                        st.write("账户昵称：**" + key + "**")
                        if str(share_data[key]['gpt4_limit']) == "-1":
                            st.write("GPT4 次数：**无限制**")
                        else:
                            st.write("GPT4 次数：**限制 - " + str(share_data[key]['gpt4_limit']) + " 次**")

                    if str(share_data[key]['gpt35_limit']) == "-1":
                        st.write("GPT3.5 次数：**无限制**")
                    else:
                        st.write("GPT3.5 次数：**限制 - " + str(share_data[key]['gpt35_limit']) + " 次**")

                    if str(share_data[key]['expires_in']) == "0":
                        st.write("账户到期时间：**永不过期**")
                    else:
                        st.write("账户到期时间：**" + str(share_data[key]['expires_in']) + "**")
                    st.write("")
        i += 1

else:
    st.write("")
    sac.alert(label="**无权限访问！**", description="**Share共享站管理员暂未开放！**", color="error", variant="filled", size="lg", radius="lg", icon=True, closable=False)
    if st.button("**返回首页**", use_container_width=True):
        st.switch_page("home.py")
    st.write("")


col4, col5, col6 = st.columns([0.2, 0.6, 0.2])

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
