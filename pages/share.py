import os
import json
import toml
import time
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

with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    web_setting = toml.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    accounts = json.load(file)
with open(current_path + '/domain.json', 'r', encoding='utf-8') as file:
    domains = json.load(file)
with open(current_path + '/users.json', 'r', encoding='utf-8') as file:
    users = json.load(file)
with open(current_path + '/openai.json', 'r', encoding='utf-8') as file:
    openai_data = json.load(file)
with open(current_path + '/anthropic.json', 'r', encoding='utf-8') as file:
    anthropic_data = json.load(file)
with open(current_path + '/share.json', 'r', encoding='utf-8') as file:
    share_data = json.load(file)
with open(style_path + "//Simple_White.html", "r", encoding="utf-8") as file:
    Simple_white_html = file.read()
with open(style_path + "//Classic_Black.html", "r", encoding="utf-8") as file:
    Classic_Black_html = file.read()
with open(style_path + "//Retro_Orange.html", "r", encoding="utf-8") as file:
    Retro_Orange_html = file.read()
    Retro_Orange_html = Retro_Orange_html.replace("{{text}}", "Spark your creativity")
with open(style_path + "//sidebar.html", "r", encoding="utf-8") as file:
    sidebar_html = file.read()


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
                    logger.info(f"【Share登录】 共享账户：{user_name} 的 SA 已经失效！")
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
                        logger.info(f"【Share登录】 共享账户：{user_name} 的 SA 刷新成功！")
                        openai_data[user_name]["token"] = token_result
                        config_json = json.dumps(openai_data, indent=2)
                        with open(current_path + 'openai.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(config_json)
                    else:
                        logger.info(f"【Share登录】 共享账户：{user_name} 的 AC 已经失效！")
                        status.update(label="**AC状态已失效！尝试刷新中...**", state="running", expanded=False)
                        ac_status, user_ac_token = get_accesstoken(accounts[group_result]["refresh_token"])
                        if ac_status:
                            logger.info(f"【Share登录】 共享账户：{user_name} 的 AC 刷新成功！")
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
                            logger.info(f"【Share登录】 共享账户：{user_name} 的 AC 刷新失败！")
                            error_status = "RF过期"
                else:
                    error_status = "过期"
            else:
                error_status = "SA过期"
        status.update(label="**环境验证成功！**", state="complete", expanded=False)
    return error_status, token_result


def check_anthropic(token_result, user_name):  # 看看始皇后续有没有大动作啦!
    return False, False


@st.experimental_dialog("身份验证")
def choose(user_name):
    del st.session_state["role"]
    st.write("")
    st.write("**欢迎使用Share共享服务！**")
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
            logger.info(f"【Share登录】 共享账户：{user_name} 登录成功！")
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
            logger.info(f"【Share登录】 共享账户：{user_name} 登录成功！")
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

if "theme" not in st.session_state:
    st.session_state.theme = web_setting["web"]["login_theme"]

if st.session_state.theme == "Simple White":
    st.markdown(Simple_white_html, unsafe_allow_html=True)
    st.markdown(f"<div class='centered-title'><h1>" + web_setting["web"]["title"] + "</h1></div><div class='centered-subtitle'><div>" + web_setting["web"]["subtitle"] + "</div></div>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    sac.alert(label=web_setting["web"]["share_notice"], color=web_setting["web"]["notice_color"], variant=web_setting["web"]["notice_style"], banner=web_setting["web"]["notice_banner"], size=web_setting["web"]["notice_size"], radius=web_setting["web"]["notice_radius"])

elif st.session_state.theme == "Classic Black":
    st.markdown(Classic_Black_html, unsafe_allow_html=True)
    st.markdown(f"<div class='centered-title'><h1>" + web_setting["web"]["title"] + "</h1></div><div class='centered-subtitle'><div>" + web_setting["web"]["subtitle"] + "</div></div>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    sac.alert(label=web_setting["web"]["share_notice"], color=web_setting["web"]["notice_color"], variant=web_setting["web"]["notice_style"], banner=web_setting["web"]["notice_banner"], size=web_setting["web"]["notice_size"], radius=web_setting["web"]["notice_radius"])

elif st.session_state.theme == "Retro Orange":
    st.markdown(Retro_Orange_html, unsafe_allow_html=True)

st.markdown("""
<style>
body {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
    background-color: #f0f0f0;
    font-family: Arial, sans-serif;
}
.tag-container {
    display: flex;
    gap: 10px;
}
.tag {
    display: inline-block;
    padding: 5px 15px;
    border-radius: 20px;
    color: black;
    font-size: 14px;
    margin: 3px;
    transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.tag:hover {
    transform: scale(1.1);
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
}
.tag-gpt-3-5 {
    background-color: #a1e49d;
    animation: glow-green 1.5s infinite alternate;
}
.tag-gpt-4 {
    background-color: #a1d4f5;
    animation: glow-blue 1.5s infinite alternate;
}
.tag-gpt-4-0 {
    background-color: #f5a1a1;
    animation: glow-red 1.5s infinite alternate;
}
.tag-claude {
    background-color: #f5c542;
    animation: glow-yellow 1.5s infinite alternate;
}
@keyframes glow-green {
    from { box-shadow: 0 0 5px #a1e49d; }
    to { box-shadow: 0 0 20px #8fd37b; }
}
@keyframes glow-blue {
    from { box-shadow: 0 0 5px #a1d4f5; }
    to { box-shadow: 0 0 20px #7fc2eb; }
}
@keyframes glow-red {
    from { box-shadow: 0 0 5px #f5a1a1; }
    to { box-shadow: 0 0 20px #eb7b7b; }
}
@keyframes glow-yellow {
    from { box-shadow: 0 0 5px #f5c542; }
    to { box-shadow: 0 0 20px #e5b128; }
}
</style>
""", unsafe_allow_html=True)

if web_setting["web"]["share"]:
    st.divider()
    st.write("")
    key = st.selectbox("**选择要登录的Share账户**", list(share_data.keys()), index=0)
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("**点我登录**", use_container_width=True, key="login1"):
            st.session_state.role = "role"
        try:
            if st.session_state.role == "role":
                choose(key)
                st.session_state.role = None
        except:
            pass

    with col2:
        if st.button("**返回首页**", use_container_width=True, key="home"):
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
                    st.markdown("<div style='display: flex; justify-content: left; align-items: left;'><b>账户：" + key + "</b></div>", unsafe_allow_html=True)
                    st.write("")
                    if share_data[key]['openai']['expires_in'] == "0" or share_data[key]['openai']['expires_in'] == 0:
                        st.markdown("<div style='display: flex; justify-content: left; align-items: left;'><b>过期时间：永不过期</b></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='display: flex; justify-content: left; align-items: left;'><b>过期时间：" + str(share_data[key]['openai']['expires_in']) + " 秒</b></div>", unsafe_allow_html=True)
                    st.divider()
                    if users[key]["allow_claude"]:
                        st.markdown(f"<div style='display: flex; justify-content: left; align-items: left;'><div class='tag tag-claude'>Claude</div>", unsafe_allow_html=True)
                        st.write("")
                    if users[key]["allow_chatgpt"]:
                        if share_data[key]['openai']['type'] == "Free":
                            st.markdown("""
                            <div style='display: flex; justify-content: left; align-items: left;'>
                            <div class='tag tag-gpt-3-5'>GPT-3.5</div>
                            <div class='tag tag-gpt-4-0'>GPT-4o*</div>
                            </div>""", unsafe_allow_html=True)
                            st.write("")
                        elif share_data[key]['openai']['type'] == "Plus":
                            st.markdown("""
                            <div style='display: flex; justify-content: left; align-items: left;'>
                            <div class='tag tag-gpt-3-5'>GPT-3.5</div>
                            <div class='tag tag-gpt-4'>GPT - 4 </div>
                            <div class='tag tag-gpt-4-0'>GPT-4o</div>
                            </div>""", unsafe_allow_html=True)
                            st.write("")
                    st.write("")

        if i % 2 == 0:
            with col2:
                with st.expander("**共享账户** " + str(i), expanded=True, icon=":material/apps:"):
                    st.write("")
                    st.markdown(
                        "<div style='display: flex; justify-content: left; align-items: left;'><b>账户：" + key + "</b></div>",
                        unsafe_allow_html=True)
                    st.write("")
                    if share_data[key]['openai']['expires_in'] == "0" or share_data[key]['openai']['expires_in'] == 0:
                        st.markdown("<div style='display: flex; justify-content: left; align-items: left;'><b>过期时间：永不过期</b></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='display: flex; justify-content: left; align-items: left;'><b>过期时间：" + str(share_data[key]['openai']['expires_in']) + " 秒</b></div>", unsafe_allow_html=True)
                    st.divider()
                    if users[key]["allow_claude"]:
                        st.markdown( f"<div style='display: flex; justify-content: left; align-items: left;'><div class='tag tag-claude'>Claude</div>", unsafe_allow_html=True)
                        st.write("")
                    if users[key]["allow_chatgpt"]:
                        if share_data[key]['openai']['type'] == "Free":
                            st.markdown("""
                            <div style='display: flex; justify-content: left; align-items: left;'>
                            <div class='tag tag-gpt-3-5'>GPT-3.5</div>
                            <div class='tag tag-gpt-4-0'>GPT-4o*</div>
                            </div>""", unsafe_allow_html=True)
                            st.write("")
                        elif share_data[key]['openai']['type'] == "Plus":
                            st.markdown("""
                            <div style='display: flex; justify-content: left; align-items: left;'>
                            <div class='tag tag-gpt-3-5'>GPT-3.5</div>
                            <div class='tag tag-gpt-4'>GPT - 4 </div>
                            <div class='tag tag-gpt-4-0'>GPT-4o</div>
                            </div>""", unsafe_allow_html=True)
                            st.write("")
                    st.write("")
        i += 1

else:
    st.write("")
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
    with col2:
        st.divider()
        sac.alert(label="**无权限访问！**", description="**Share共享站管理员暂未开放！**", color="error", variant="filled", size="lg", radius="lg", icon=True, closable=False)
        if st.button("**返回首页**", use_container_width=True, key="home2"):
            st.switch_page("home.py")
        st.write("")


with open(style_path + "//footer.html", "r", encoding="utf-8") as file:
    footer_html = file.read()
    color = "white"
    if st.session_state.theme == "Retro Orange":
        color = "#efede4"
    footer_html = footer_html.replace("{{color}}", color)
st.markdown(footer_html, unsafe_allow_html=True)
st.logo("LOGO.png", link="https://github.com/Chenyme/oaifree-tools")

