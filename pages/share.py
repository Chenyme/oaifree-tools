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

if web_setting["web"]["button_style"] == "Classic-black":
    st.markdown("""
        <style>
        .st-emotion-cache-keje6w.e1f1d6gn3 {
            float: left !important;
            text-align: left !important;
            display: inline-block;
        }
        .st-emotion-cache-1vt4y43 {
            background-color:  white !important;
            color: black !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
        }
        .eyeqlp52.st-emotion-cache-1pbsqtx.ex0cdmw0 {
            fill: black !important;
        }
        .st-emotion-cache-consg2.e16zdaao0 {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 2.5em;
            background-color: #333 !important;
            color: #fff !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
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
        .stButton>button {
            width: 100%;
            height: 2.5em;
            background-color: #333;
            color: #fff;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
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
    button_type = "secondary"

elif web_setting["web"]["button_style"] == "Simple-white":
    st.markdown("""
        <style>
        .st-emotion-cache-keje6w.e1f1d6gn3 {
            float: left !important;
            text-align: left !important;
            display: inline-block;
        }
        .st-emotion-cache-1vt4y43 {
            background-color:  white !important;
            color: black !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
        }
        .eyeqlp52.st-emotion-cache-1pbsqtx.ex0cdmw0 {
            fill: black !important;
        }
        .st-emotion-cache-consg2.e16zdaao0 {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 2.5em;
            background-color: white !important;
            color: black !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
            font-size: 1em;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease, color 0.2s ease;
            text-decoration: none;
            padding: 0 1em;
        }
        .st-emotion-cache-consg2.e16zdaao0:hover {
            background-color: #f0f0f0 !important;
            color: black !important;
            transform: scale(1.05);
        }
        .st-emotion-cache-consg2.e16zdaao0:active {
            background-color: #e0e0e0 !important;
            color: black !important;
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
        .stButton button {
            width: 100%;
            height: 2.5em;
            background-color: white !important;
            color: black !important;
            border: 1px solid """ + web_setting["web"]["button_border"] + """ !important;
            border-radius: """ + str(web_setting["web"]["button_border_radius"]) + """px !important;
            font-size: 1em !important;
            cursor: pointer !important;
            transition: background-color 0.3s ease, transform 0.2s ease, color 0.2s ease;
            padding: 0.5em 1em !important;
        }
        .stButton button:hover {
            background-color: #f0f0f0 !important;
            color: black !important;
            transform: scale(1.05) !important;
        }
        .stButton button:active {
            background-color: #e0e0e0 !important;
            color: black !important;
            transform: scale(0.95) !important;
        }
        </style>
        """, unsafe_allow_html=True)  # 按钮设置
    button_type = "secondary"

elif web_setting["web"]["button_style"] == "Primary":
    button_type = "primary"
else:
    button_type = "secondary"

footer = """
<style>
.footer {
    position: fixed;
    bottom: 0;
    right: 0;
    padding: 10px;
    font-size: 14px;
    color: #555;
}
.footer p {
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
}
.footer a {
    color: #0073e6;
    text-decoration: none;
    transition: color 0.3s ease;
}
.footer a:hover {
    color: #005bb5;
}

/* Media query for mobile devices */
@media (max-width: 768px) {
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        left: 0;
        margin: 0 auto;
        width: 100%;
        background-color: white;
        border-top: 1px solid #ddd;
        justify-content: center;
        text-align: center;
    }
}
</style>
<div class="footer">
    <p><strong>Powered by <a href="https://zhile.io/" target="_blank">@Neo</a>，</strong> 
    <strong>Created by <a href="https://github.com/Chenyme" target="_blank">@Chenyme</a></strong></p>
</div>
"""


def check_login_status(token_result, user_name, group_result):
    error_status = False
    # 判断SA_Token是否有效
    with st.status("**正在验证您的环境...**") as status:

        if check_sharetoken(token_result):
            st.session_state.role = None
            token_result = token_result
            logger.info(f"【Share登录】 共享账户：{user_name} 登录成功！")
        else:
            if web_setting["web"]["refresh_all"]:
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
                        logger.info(f"【Share登录】 共享账户：{user_name} 登录成功！")
                    else:
                        logging.info(f"<用户> 【AC刷新】 用户 {user_name} 的AC_Token已经失效！尝试刷新中...")
                        status.update(label="**AC状态已失效！尝试刷新中...**", state="running", expanded=False)
                        ac_status, user_ac_tk = get_accesstoken(accounts[group_result]["refresh_token"])

                        # 判断RF_Token是否有效
                        if ac_status:
                            logger.info(f"【Share登录】 共享账户：{user_name} 登录成功！")
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
                            logging.error(f"<用户> 【AC刷新】 用户组 {group_result} 的AC_Token刷新失败！请检查RF_Token是否正确！")
                else:
                    error_status = "过期"
                    logging.error(f"<用户> 【SA验证】 用户 {user_name} 的SA_Token已经过期！")
            else:
                error_status = "SA已过期"
                logging.error(f"<用户> 【SA验证】 用户 {user_name} 的SA_Token已经过期！")
        status.update(label="**环境验证成功！**", state="complete", expanded=False)
    return error_status, token_result


@st.experimental_dialog("状态验证")  # 选择模块
def choose(user_name, login_result, token_result, group_result):
    st.write(f"## 欢迎使用共享服务！")
    st.divider()
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
            elif error_status == "SA已过期":
                status.update(label="**啊哦！出错了！**", state="error", expanded=True)
                st.write("")
                sac.alert(label="**SA已过期，请联系管理员续费！**", color="error", variant="filled", size="md", radius="md", icon=True, closable=True)
            else:
                status.update(label="**即将验证完毕...感谢您的等待！**", state="running", expanded=False)
                domain = web_setting["web"]["domain"]

                if domain_data[domain]['type'] == "Classic":
                    url = "https://" + domain + "/auth/login_share?token=" + token_result
                else:
                    url = get_login_url(domain, token_result)

                st.write("")
                st.link_button("**开始使用**", url, use_container_width=True, type=button_type)
                status.update(label="**用户验证成功!**", state="complete", expanded=True)
                st.write("")

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
                    name = domain_data[domain]['name']
                    st.link_button(f"**{name}**", url, use_container_width=True, type=button_type)
                status.update(label="**用户验证成功!**", state="complete", expanded=True)
            st.write("")
        st.write("")


st.markdown(
    """
    <style>
    .centered-title {
        position: relative;
        top: -60px;
        text-align: center;
        margin-bottom: 0; 
        font-size: 2em;
    }
    .centered-subtitle {
        text-align: center;
        margin-top: -50px;
        font-size: 1em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(f"<div class='centered-title'><h1>" + web_setting["web"][
    "title"] + "</h1></div><div class='centered-subtitle'><div>" + web_setting["web"]["subtitle"] + "</div></div>",
            unsafe_allow_html=True)

st.write("")
st.write("")
sac.alert(label=web_setting["web"]["share_notice"], color=web_setting["web"]["notice_color"], variant=web_setting["web"]["notice_style"], banner=web_setting["web"]["notice_banner"], size=web_setting["web"]["notice_size"], radius=web_setting["web"]["notice_radius"])
st.logo("LOGO.png", link="https://github.com/Chenyme/oaifree-tools")
if web_setting["web"]["share"]:
    st.divider()
    st.write("")
    key = st.selectbox("**选择要登录的Share账户**", list(share_data.keys()), index=0)
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("**点我登录**", use_container_width=True, key="login1", type=button_type):
            st.session_state.role = "role"
        try:
            if st.session_state.role == "role":
                choose(key, True, share_data[key]['token'], share_data[key]['group'])
                st.session_state.role = None
        except:
            pass

    with col2:
        if st.button("**返回首页**", use_container_width=True, key="home", type=button_type):
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
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
    with col2:
        st.divider()
        sac.alert(label="**无权限访问！**", description="**Share共享站管理员暂未开放！**", color="error", variant="filled", size="lg", radius="lg", icon=True, closable=False)
        if st.button("**返回首页**", use_container_width=True, key="home2", type=button_type):
            st.switch_page("home.py")
        st.write("")

st.markdown(footer, unsafe_allow_html=True)  # 底部信息,魔改请勿删除
