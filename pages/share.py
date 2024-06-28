import os
import json
import toml
import logging
import streamlit as st
import streamlit_antd_components as sac
from utils import get_login_url

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

st.set_page_config(page_title=web_setting["web"]["title"], page_icon="LOGO.png")

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

    st.write("")
    st.write("")
    st.write("")
    key = st.selectbox("**选择要登录的Share账户**", list(share_data.keys()), index=0)
    st.write("")
    if st.button("登录", use_container_width=True, key="login1"):
        logger.info(f"【Share登录】 共享账户：{key} 被登录！")
        domain = web_setting["web"]["domain"]
        share_url = get_login_url(domain, share_data[key]['token'])
        st.link_button("**点我验证**", share_url, use_container_width=True, type="primary")
        st.write("")
else:

    st.write("")
    sac.alert(label="**无权限访问！**", description="**Share共享站管理员暂未开放！**", color="red", variant="filled", size="lg", radius="lg", icon=True, closable=False)
    if st.button("**返回首页**", use_container_width=True):
        st.switch_page("home.py")
    st.write("")

    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
    with col2:
        st.image("LOGO.png", width=200, caption="Shared共享服务", use_column_width=True)

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
