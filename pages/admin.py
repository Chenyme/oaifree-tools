# -*- coding: utf-8 -*-
# v1.1.4 @Chenyme
import os
import re
import time
import json
import toml
import base64
import secrets
import logging
import zipfile
import requests
from datetime import datetime
from io import BytesIO
import pandas as pd
import altair as alt
import streamlit as st
import streamlit_antd_components as sac
from utils import get_accesstoken, get_sharetoken, df_to_json1, df_to_json2, df_to_json3, df_to_json4, check_sharetoken, get_size

# 运行日志
current_path = os.path.abspath('.') + '/config/'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(current_path + "/app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

# 读取配置文件
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
with open(current_path + '/refresh.json', 'r', encoding='utf-8') as file:
    refresh_data = json.load(file)
with open("LOGO.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

version = "v1.1.5"

st.set_page_config(layout="wide", page_title=web_setting["web"]["title"], page_icon="LOGO.png")

if web_setting["web"]["button_style"] == "Classic-black":
    st.markdown("""
        <style>
        .st-emotion-cache-keje6w.e1f1d6gn3 {
            float: right !important;
            text-align: right !important;
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
        .stDownloadButton>button {
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
        .stDownloadButton>button:hover {
            background-color: #444;
            color: #fff;
            transform: scale(1.05);
        }
        .stDownloadButton>button:active {
            background-color: #222;
            color: #fff;
            transform: scale(0.95);
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
            float: right !important;
            text-align: right !important;
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
        .stDownloadButton>button:hover {
            background-color: #444;
            color: #fff;
            transform: scale(1.05);
        }
        .stDownloadButton>button:active {
            background-color: #222;
            color: #fff;
            transform: scale(0.95);
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

st.logo("LOGO.png", link="https://github.com/Chenyme/oaifree-tools")

# 阻止非法访问
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role == "admin":

    @st.experimental_dialog("安全保护")
    def key():
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; align-items: center;">
                <img src="data:image/png;base64,{encoded_image}" alt="LOGO" style="width: 100px;">
                <p style="text-align: center; color: gray; font-size: 12px; margin-top: -20px;">{version}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        sac.alert(label='**首次登入请修改super_key(管理员密钥)**', color="info", size='sm', radius='sm', icon=True, variant="filled")
        new_super_user = st.text_input("**新的昵称**", placeholder="请输入您的新昵称！")
        new_super_key = st.text_input("**新的密钥**", type="password", placeholder="请输入您的新密钥！")

        sac.divider(align="center", key="divider_safe")
        if st.button("**保存更改**", use_container_width=True, type=button_type):
            if new_super_user == "" or new_super_user is None:
                sac.alert(label="**昵称不允许为空，请重新输入！**", color="error", variant='filled', size="sm", radius="sm", icon=True, closable=True)
            elif len(new_super_key) < 8:
                sac.alert(label="**密钥不允许少于8位，请重新输入！**", color="error", variant='filled', size="sm", radius="sm", icon=True, closable=True)
            elif new_super_key == "12345678":
                sac.alert(label="**密钥不允许为默认密钥，请重新输入！**", color="error", variant='filled', size="sm", radius="sm", icon=True, closable=True)
            else:
                web_setting["web"]["super_user"] = new_super_user
                web_setting["web"]["super_key"] = new_super_key
                sac.alert(label="**更改成功！**", color="success", variant='filled', size="sm", radius="sm", icon=True, closable=True)
                sac.alert(label="**即将自动刷新页面！**", color="success", variant='filled', size="sm", radius="sm", icon=True, closable=True)
                logger.info(f"<管理员> 【密钥修改】 修改了新的密钥！")
                with open(current_path + "/setting.toml", "w", encoding="utf-8") as file:
                    toml.dump(web_setting, file)
                time.sleep(1)
                st.rerun()
        st.write("")
    @st.experimental_dialog("使用说明")
    def readme():
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; align-items: center;">
                <img src="data:image/png;base64,{encoded_image}" alt="LOGO" style="width: 100px;">
                <p style="text-align: center; color: gray; font-size: 12px; margin-top: -20px;">{version}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("""
            - **制作不易，不许白嫖，请给一颗免费的心叭！开源项目可自由魔改，但请保留原作者信息并遵循开源协议。**
            - **OaiT 管理后台支持管理功能：**
            
                - **个性化**：站点标题/站点公告/登录主题/按钮样式
                - **站点工具**：登录统计/运行日志/站点迁移
                - **账户管理**：账号/用户/共享池/管理/各类Token刷新
                - **域名管理**：负载分流/新旧UI/延迟测速/自定义域名
                - **UID 标识**：UID标识/UID登录/UID改密/
                - **授权令牌**：邀请令牌(注册)/刷新令牌(续费)
                - **TOKEN 刷新**：自动刷新SA_Token/AC_Token
                
            ---
            - **注意事项：**
                - 新版本配置文件可能不同，导入时请注意版本兼容性
                - 修改后请及时检查并保存，否则可能会导致数据丢失
                - 新增账户注意用户组命名，不可重复，否则会自动覆盖
                - **若使用中框内出现 "Press Enter To Apply" 字样，请及时按回车或点击页面空白处以确认，否则可能登录失败！**
                
            ---
            - **特别鸣谢：**
                - **感谢 Neo 的付出，为我们提供了方便快捷的GPT服务。**
                - **我是Chenyme，期待我们的下次相遇！**
            # OpenAI，Not CloseAI！愿开源精神永存！
            ---
        """)

        if st.button("**我已知晓，不再弹出**", use_container_width=True, type=button_type):
            web_setting["web"]["readme"] = True
            with open(current_path + "/setting.toml", "w", encoding="utf-8") as file:
                toml.dump(web_setting, file)
            st.rerun()
        st.link_button("**来GitHub给我一颗星叭！**", "https://github.com/Chenyme/oaifree-tools", use_container_width=True, type=button_type)

    @st.experimental_dialog("站点迁移 - 配置导出")
    def download():
        sac.alert(label="**号池数据：`account.json` ; 用户数据：`config.json` ;**\n\n**共享数据：`share.json` ; 域名数据：`domain.json` ;**\n\n**邀请令牌：`invite.json` ; 刷新令牌：`refresh.json` ;**\n\n**站点配置：`setting.toml` ; 服务日志：`app.log`**", color="info", variant='quote', size="md", radius="sm")
        st.write("**需要导出的数据：**")
        files = st.multiselect("文件", ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json", "app.log", "refresh.json", "domain.json"], ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json", "app.log", "refresh.json", "domain.json"], label_visibility="collapsed")
        if st.button("**导出数据**", use_container_width=True, type=button_type):
            directory_path = current_path
            zip_buffer = BytesIO()
            try:
                sac.alert(label="**正在准备站点数据，请耐心等待...**", color="info", variant='filled', size="sm", radius="sm", icon=True)
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for root, _, _ in os.walk(directory_path):
                        for config_file in files:
                            file_path = os.path.join(root, config_file)
                            data_name = os.path.relpath(file_path, directory_path)
                            zip_file.write(file_path, data_name)
                zip_buffer.seek(0)

                col1, col2 = st.columns(2)
                i = 1
                for file in files:
                    if i % 2 == 1:
                        with col1:
                            sac.alert(label=f"**{file}**", color="success", variant='filled', size="sm", radius="lg", icon=True)
                    if i % 2 == 0:
                        with col2:
                            sac.alert(label=f"**{file}**", color="success", variant='filled', size="sm", radius="lg", icon=True)
                    i += 1

                st.download_button(label="**点我下载**", data=zip_buffer, file_name="config.zip", mime="application/zip", use_container_width=True, type=button_type)
            except:
                sac.alert(label="导出时出错，请重试！", color="error", variant='filled', size="sm", radius="sm", icon=True, closable=True)

    @st.experimental_dialog("站点迁移-配置导入")
    def upload():
        sac.alert(label="**仅支持V1.1.4版本后的配置文件**", description=" 上传V1.1.3版本配置时，请删除zip中的冲突文件：**`setting.toml`**，更低版本请慎重上传！ ", banner=True, color="info", variant='filled', size="md", radius="sm")
        st.write("**请上传配置文件**")
        uploaded_file = st.file_uploader("上传文件", type=['zip'], label_visibility="collapsed")
        required_files = ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json", "app.log", "refresh.json", "domain.json"]
        if st.button("**开始数据迁移**", use_container_width=True, type=button_type):
            if uploaded_file is not None:
                zip_buffer = BytesIO(uploaded_file.getvalue())
                with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                    zip_file_list = zip_ref.namelist()
                    success_files = [file for file in required_files if file in zip_file_list]
                    error_files = [file for file in zip_file_list if file not in required_files]
                    sac.alert(label="**正在迁移数据，请稍后...**", color="info", variant='filled', size="sm", radius="sm", icon=True, closable=True)
                    col1, col2 = st.columns(2)
                    i = 1
                    for file in success_files:
                        zip_ref.extract(file, current_path)
                        if i % 2 == 1:
                            with col1:
                                sac.alert(label=f"**{file}**", color="success", variant='filled', size="sm", radius="lg", icon=True)
                        if i % 2 == 0:
                            with col2:
                                sac.alert(label=f"**{file}**", color="success", variant='filled', size="sm", radius="lg", icon=True)
                        i += 1
                    for file in error_files:
                        sac.alert(label=f"**未知文件 {file}**", color="error", variant='filled', size="sm", radius="lg", icon=True)
                sac.alert(label="**迁移成功，请及时刷新界面！若出现错误，请检查数据兼容性！**", banner=True, color="success", variant='filled', size="sm", radius="lg", icon=True)
            else:
                sac.alert(label="**请上传需要迁移的数据！**", color="error", variant='filled', size="sm", radius="sm", icon=True)

    @st.experimental_dialog("新增账户")
    def new_account():
        col1, col2 = st.columns(2)
        with col1:
            new_group = st.text_input("**命名新用户组***", value="", help="所有模块串联的唯一标识，不可为空", placeholder="唯一标识，不可为空！")
        with col2:
            new_account_type = st.selectbox("**账户订阅类型***", ["Free", "Plus"], index=1, help="订阅套餐情况，不可为空！")
        new_account = st.text_input("**账户邮箱**", value="", help="账户邮箱，用于标识备注，可为空", placeholder="账户邮箱，仅用于自我备注，可为空！")
        new_access_token = st.text_input("**AC_Token***", help="AC_Token，刷新时的重要Token，不可为空", placeholder="AC_Token，刷新时的重要Token，不可为空！")
        new_refresh_token = st.text_input("**RF_Token**", help="RF_Token，AC刷新的重要Token，可为空，为空则刷新功能不可用", placeholder="RF_Token，AC刷新的重要Token！若无，可为空！")
        st.write("")
        if st.button("**新增此账户**", use_container_width=True, type=button_type):
            if new_group in accounts.keys():
                sac.alert(label="**用户组命名重复！请重新命名！**", color="error", variant='filled', size="sm", radius="sm", icon=True)
            elif new_group == "":
                sac.alert(label="**用户组不可为空！请重新命名！**", color="error", variant='filled', size="sm", radius="sm", icon=True)
            elif new_access_token == "":
                sac.alert(label="**AC_Token不可为空！请重新填写！**", color="error", variant='filled', size="sm", radius="sm", icon=True)
            elif new_refresh_token == "":
                sac.alert(label="**RF_Token不可为空！请重新填写！**", color="error", variant='filled', size="sm", radius="sm", icon=True)
            else:
                accounts[new_group] = {
                    "account_type": new_account_type,
                    "account": new_account,
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                }
                with open(current_path + "accounts.json", "w", encoding="utf-8") as file:
                    json.dump(accounts, file, indent=2)
                logger.info(f"<管理员> 【账户新增】 新增用户组:{new_group}，账户订阅:{new_account_type}，账户邮箱:{new_account}")
                sac.alert(label="**账户新增成功！**", color="success", variant='filled', size="md", radius="lg", icon=True)
                time.sleep(1)
                st.rerun()

    @st.experimental_dialog("新用户权限")
    def invite():
        site_limit = st.text_input("**网站限制**", value=web_setting["web"]["site_limit"], help="限制的网站, 为空则不限制", placeholder="限制的网站, 为空则不限制")
        expires_in = st.number_input("**有效期（秒）**", value=web_setting["web"]["expires_in"], min_value=0, max_value=864000, step=86400, help="token有效期（单位为秒），填 0 则永久有效")
        gpt35_limit = st.number_input("**限制GPT-3.5次数**", value=web_setting["web"]["gpt35_limit"], min_value=-1, max_value=1000000, step=5, help="GPT-3.5对话限制，填 -1 则不限制")
        gpt4_limit = st.number_input("**限制GPT-4次数**", value=web_setting["web"]["gpt4_limit"], min_value=-1, max_value=1000000, step=5, help="GPT-4对话限制，填 -1 则不限制")
        show_conversations = st.selectbox("会话无需隔离", ['true', 'false'], index=['true', 'false'].index(web_setting["web"]["show_conversations"]), help="false为隔离会话")
        st.write("")
        if st.button("**保存新用户权限**", use_container_width=True, type=button_type):
            web_setting["web"]["site_limit"] = site_limit
            web_setting["web"]["expires_in"] = expires_in
            web_setting["web"]["gpt35_limit"] = gpt35_limit
            web_setting["web"]["gpt4_limit"] = gpt4_limit
            web_setting["web"]["show_conversations"] = show_conversations
            with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                toml.dump(web_setting, f)
            logger.info(f"<管理员> 【邀请码设置】 更新了邀请码的默认设置！")
            sac.alert(label="修改新用户权限成功！", color="success", variant='filled', size="md", radius="lg", icon=True)

    @st.experimental_dialog("生成邀请令牌")
    def new_invite():
        st.write("")
        it_group = st.selectbox("**选择用户组**", list(accounts.keys()), index=0)
        note = st.text_input("**备注**", placeholder="2024/06/30 00:00:00", help="备注信息，可为空")
        auto_it_gen = st.checkbox("**批量生成**")
        if auto_it_gen:
            num_it_gen = st.number_input("**生成数量**", value=5, min_value=1, max_value=100, step=5)
            len_it_gen = st.number_input("**邀请令牌长度**", value=16, min_value=16, max_value=32)
        else:
            it_token = st.text_input("**邀请令牌**", placeholder="it-xxxxxxxxxxxxxxxx")

        st.write("")
        if st.button("**生成邀请令牌**", use_container_width=True, key="new_invite_token_gen", type=button_type):
            if auto_it_gen:
                for i in range(num_it_gen):
                    invite_config["it-" + secrets.token_urlsafe(len_it_gen)] = {
                        "group": it_group,
                        "note": note,
                        "used": False
                    }
                with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                    json.dump(invite_config, f, indent=2)

                logger.info(f"<管理员> 【邀请令牌】 生成了{num_it_gen}个新的邀请令牌！")
                sac.alert(label="**生成成功！**", color="success", variant='filled', size="sm", radius="lg", icon=True)
                time.sleep(0.5)
                sac.alert(label="**即将自动刷新！**", color="success", variant='filled', size="sm", radius="lg", icon=True)
                time.sleep(1)
                st.rerun()
            elif it_token is None or it_token == "":
                sac.alert(label="**邀请令牌不能为空，请重新填写！**", color="error", variant='filled', size="sm", radius="sm", icon=True)
            elif it_token in invite_config.keys():
                sac.alert(label="**此邀请令牌已存在，请重新填写！**", color="error", variant='filled', size="sm", radius="sm", icon=True)
            else:
                invite_config[it_token] = {
                    "group": it_group,
                    "note": note,
                    "used": False
                }
                logger.info(f"<管理员> 【邀请令牌】 生成了新的邀请令牌：{it_token}！")
                with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                    json.dump(invite_config, f, indent=2)
                sac.alert(label="**生成成功！**", color="success", variant='filled', size="sm", radius="lg", icon=True)
                time.sleep(0.5)
                sac.alert(label="**即将自动刷新！**", color="success", variant='filled', size="sm", radius="lg", icon=True)
                time.sleep(1)
                st.rerun()

    @st.experimental_dialog("状态刷新")
    def refresh_user():
        st.write("")
        st.write("**账户状态检测**")
        col1, col2 = st.columns([0.8, 0.2])
        with col2:
            if st.checkbox("全选", key="all"):
                default = list(config.keys())
            else:
                default = []
        with col1:
            status_list = st.multiselect("检测用户", list(config.keys()), default=default, key="status_list", label_visibility="collapsed")

        st.write("")
        if st.button("**状态检测**", use_container_width=True, key="check_user_account", type=button_type):
            if len(status_list) != 0:
                sc_list = []
                er_list = []
                for user in status_list:
                    status = check_sharetoken(config[user]["token"])
                    if status:
                        sc_list.append(user)
                    else:
                        er_list.append(user)
                if len(sc_list) == 0:
                    sac.alert(label="**所有账户状态正常！**", color="success", variant="filled", size="sm", radius="lg", icon=True)
                else:
                    df_result = pd.DataFrame({"成功": pd.Series(st.session_state.sc_list), "失败": pd.Series(st.session_state.er_list)})
                    st.data_editor(df_result, hide_index=True, use_container_width=True, height=143)
            else:
                sac.alert(label="**请先选择需要检测的账户！**", color="warning", variant="filled", size="sm", radius="sm", icon=True)

        st.divider()
        st.write("**需要刷新的账户**")
        user_group = st.multiselect("刷新的用户", st.session_state.er_list, key="user_groups", label_visibility="collapsed")
        st.write("")
        if st.button("**刷新状态**", use_container_width=True, type=button_type):
            if len(user_group) != 0:
                for user in user_group:
                    status, name, token_key = get_sharetoken(user_group, accounts[config[user]["group"]]["access_token"], config[user]["site_limit"], config[user]["expires_in"], config[user]["gpt35_limit"], config[user]["gpt4_limit"], config[user]["show_conversations"])
                    if status:
                        config[user]["token"] = token_key
                        with open(current_path + '/config.json', 'w', encoding='utf-8') as file:
                            json.dump(config, file, indent=2)
                        sac.alert(label="**{user} 刷新成功！**", color="success", variant="filled", size="sm", radius="lg", icon=True)
                        logger.info(f"<管理员> 【账户刷新】 账户：{user} 刷新成功！")
                    else:
                        sac.alert(label=f"**{user} 刷新失败！**", color="error", variant="filled", size="sm", radius="sm", icon=True)
                        logger.error(f"<管理员> 【账户刷新】 账户：{user} 刷新失败！请检查AC_Token是否有效！")
            else:
                sac.alert(label="**请先状态检测，失效账户才能刷新！**", color="warning", variant="filled", size="sm", radius="sm", icon=True)

    @st.experimental_dialog("生成刷新令牌")
    def new_refresh():
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            rf_group = st.selectbox("**用户组别**", accounts.keys(), key="rf_group_new")
            site_limit = st.text_input("**限制网站（为空不限制）**", value="", help="限制的网站, 为空则不限制", key="site_limit_new", placeholder="限制网站, 为空则不限制")
            expires_in = st.number_input("**有效期（秒**）", value=0, help="token有效期（单位为秒），填 0 则永久有效", key="expires_in_new")
        with col2:
            gpt35_limit = st.number_input("**限制GPT-3.5次数**", value=-1, help="GPT-3.5对话限制，填 -1 则不限制", key="gpt35_limit_new")
            gpt4_limit = st.number_input("**限制GPT-4次数**", value=-1, help="GPT-4对话限制，填 -1 则不限制", key="gpt4_limit_new")
            show_conversations = st.selectbox("**会话无需隔离**", ['true', 'false'], index=1, help="false为隔离会话", key="show_conversations_new")
        note = st.text_input("**备注**", help="备注信息，可为空", key="note_new", placeholder="2024/06/30 00:00:00")
        auto_rf_gen = st.checkbox("**批量生成**")
        if auto_rf_gen:
            num_rf_gen = st.number_input("**生成数量**", value=5, min_value=1, max_value=100, step=5, key="num_rf_gen_new")
            len_rf_gen = st.number_input("**刷新令牌长度**", value=16, min_value=16, max_value=32, key="len_rf_gen_new")
        else:
            rf_token = st.text_input("**刷新令牌**", key="rf_token_new", placeholder="rf-xxxxxxxxxxxxxxxx")

        st.write("")
        if st.button("**生成刷新令牌**", use_container_width=True, key="new_refresh", type=button_type):
            if auto_rf_gen:
                for i in range(num_rf_gen):
                    refresh_data["rf-" + secrets.token_urlsafe(len_rf_gen)] = {
                        "group": rf_group,
                        "site_limit": site_limit,
                        "expires_in": expires_in,
                        "gpt35_limit": gpt35_limit,
                        "gpt4_limit": gpt4_limit,
                        "show_conversations": show_conversations,
                        "note": note,
                        "used": False
                    }
                logger.info(f"<管理员> 【刷新令牌】 生成了{num_rf_gen}个新的刷新令牌！")
                with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                    json.dump(refresh_data, f, indent=2)
                sac.alert(label="**生成成功！**", color="success", variant='filled', size="md", radius="lg", icon=True)
                time.sleep(0.5)
                sac.alert(label="**即将自动刷新！**", color="success", variant='filled', size="md", radius="lg", icon=True)
                time.sleep(1)
                st.rerun()
            elif rf_token is None or rf_token == "":
                sac.alert(label="**刷新令牌不允许为空，请重新填写！**", color="error", variant='filled', size="sm", radius="sm", icon=True)
            elif rf_token in refresh_data.keys():
                sac.alert(label="**刷新令牌已存在，请重新填写！**", color="error", variant='filled', size="sm", radius="sm", icon=True)
            else:
                refresh_data[rf_token] = {
                    "group": rf_group,
                    "site_limit": site_limit,
                    "expires_in": expires_in,
                    "gpt35_limit": gpt35_limit,
                    "gpt4_limit": gpt4_limit,
                    "show_conversations": show_conversations,
                    "note": note,
                    "used": False
                }
                logger.info(f"<管理员> 【刷新令牌】 生成了新的刷新令牌：{rf_token}！")
                with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                    json.dump(refresh_data, f, indent=2)
                sac.alert(label="**生成成功！**", color="success", variant='filled', size="md", radius="lg", icon=True,)
                time.sleep(0.5)
                sac.alert(label="**即将自动刷新！**", color="success", variant='filled', size="md", radius="lg", icon=True)
                time.sleep(1)
                st.rerun()

    st.write("### 欢迎，" + web_setting["web"]["super_user"] + "！")

    set_choose = sac.segmented(
        items=[
            sac.SegmentedItem(label='运行日志', icon='file-text'),
            sac.SegmentedItem(label='基本设置', icon='gear-fill'),
            sac.SegmentedItem(label='号池管理', icon='pc-display'),
            sac.SegmentedItem(label='用户管理', icon='person-fill-gear'),
            sac.SegmentedItem(label='更多功能', icon='tools'),
        ], align='center', use_container_width=True, color='dark'
    )

    if set_choose == '运行日志':
        if web_setting["web"]["super_key"] == "12345678":
            key()

        with st.container(border=True):

            st.write("**站点信息**")
            user_names = config.keys()
            size_bytes1 = os.path.getsize(current_path + "app.log")
            size_bytes2 = 0
            for file in os.listdir("config"):
                if file != "app.log":
                    size_bytes2 += os.path.getsize("config/" + file)
            size1 = get_size(size_bytes1)
            size2 = get_size(size_bytes2)

            if "count_people" not in st.session_state:
                st.session_state.count_people = "正在统计"
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("用户总数", len(user_names), len(user_names)-3)
            col2.metric("号池总数", len(accounts.keys()), len(accounts.keys())-1)
            col3.metric("服务累计", st.session_state.count_people, st.session_state.count_people)
            col4.metric("日志信息", size1, size_bytes1-36)
            col5.metric("配置信息", size2, size_bytes2-4937)

            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                if st.button("**导出配置**", use_container_width=True, type=button_type):
                    download()
            with col2:
                if st.button("**导入配置**", use_container_width=True, type=button_type):
                    upload()

            st.divider()
            with open(current_path + 'app.log', 'r', encoding='utf-8') as file:
                lines = file.readlines()
            with open(current_path + 'app.log', 'r', encoding='utf-8') as file:
                logs = file.read()

            pattern_user = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【用户登录】 用户：(\w+) 登录成功！')
            pattern_share = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【Share登录】 共享账户：(\w+) 登录成功！')
            pattern_sign = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【用户注册】 新用户：(\w+) 注册成功！')

            matches_user = pattern_user.findall(logs)
            matches_share = pattern_share.findall(logs)
            matches_sign = pattern_sign.findall(logs)

            all_dates = [datetime.strptime(date, '%Y-%m-%d %H').date() for date, _ in matches_user + matches_share + matches_sign]
            min_date = min(all_dates) if all_dates else datetime.today().date()
            max_date = max(all_dates) if all_dates else datetime.today().date()

            st.write('**服务总览**')
            with st.expander("**图表工具**", expanded=False, icon=":material/square_foot:"):
                plot_choose = sac.segmented(
                    items=[
                        sac.SegmentedItem(label='登录统计总览图', icon='bar-chart-line'),
                        sac.SegmentedItem(label='用户服务统计图', icon='person-video3'),
                        sac.SegmentedItem(label='共享服务统计图', icon='share'),
                        sac.SegmentedItem(label='注册人数统计图', icon='door-open'),
                        sac.SegmentedItem(label='时段人数统计图', icon='database-fill-check'),
                    ], color='dark', use_container_width=True
                )

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    try:
                        start_date = st.date_input("**开始日期**", value=web_setting["chart"]["start_date"], min_value=min_date, max_value=max_date)
                    except:
                        start_date = st.date_input("**开始日期**", value=datetime.today().date(), min_value=min_date, max_value=max_date)
                with col2:
                    try:
                        end_date = st.date_input("**结束日期**", value=web_setting["chart"]["end_date"], min_value=min_date, max_value=max_date)
                    except:
                        end_date = st.date_input("**结束日期**", value=datetime.today().date(), min_value=min_date, max_value=max_date)
                with col3:
                    height = st.number_input('**图表高度**', value=web_setting["chart"]["height"], min_value=100, max_value=1000, step=50)
                with col4:
                    horizontal = st.selectbox('**水平显示**', [True, False], index=[True, False].index(web_setting["chart"]["horizontal"]))
                with col5:
                    st.write("")
                    st.write("")
                    if st.button("**保存设置**", use_container_width=True, type=button_type):
                        web_setting["chart"]["start_date"] = start_date
                        web_setting["chart"]["end_date"] = end_date
                        web_setting["chart"]["height"] = height
                        web_setting["chart"]["horizontal"] = horizontal
                        with open(current_path + "/setting.toml", "w", encoding="utf-8") as f:
                            toml.dump(web_setting, f)
                        st.toast("**更改成功！**", icon=":material/check_circle:")

            data_user = pd.DataFrame(matches_user, columns=['日期时间', 'user'])
            data_share = pd.DataFrame(matches_share, columns=['日期时间', 'user'])
            data_sign = pd.DataFrame(matches_sign, columns=['日期时间', 'user'])

            data_user['日期'] = pd.to_datetime(data_user['日期时间']).dt.date
            data_share['日期'] = pd.to_datetime(data_share['日期时间']).dt.date
            data_sign['日期'] = pd.to_datetime(data_sign['日期时间']).dt.date

            filtered_user = data_user[(data_user['日期'] >= start_date) & (data_user['日期'] <= end_date)]
            filtered_share = data_share[(data_share['日期'] >= start_date) & (data_share['日期'] <= end_date)]
            filtered_sign = data_sign[(data_sign['日期'] >= start_date) & (data_sign['日期'] <= end_date)]

            if plot_choose == '登录统计总览图':
                if not filtered_user.empty or not filtered_share.empty:
                    st.markdown('<div style="text-align: center; font-weight: bold; font-size: 20px;">登录统计总览图</div>', unsafe_allow_html=True)
                    st.write("")
                    matches = pd.concat([filtered_user, filtered_share])
                    st.session_state.count_people = len(matches)
                    matches['日期'] = matches['日期'].astype(str)
                    summary = matches.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
                else:
                    st.write("")
                    sac.alert("**暂无此项统计数据，快去使用吧！**", color="info", variant="filled", size="sm", radius="sm", icon=True, key="alert_1")

            if plot_choose == '用户服务统计图':

                if not filtered_user.empty:
                    st.markdown('<div style="text-align: center; font-weight: bold; font-size: 20px;">用户服务统计图</div>', unsafe_allow_html=True)
                    st.write("")
                    filtered_user['日期'] = filtered_user['日期'].astype(str)
                    summary = filtered_user.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
                else:
                    st.write("")
                    sac.alert("**暂无此项统计数据，快去使用吧！**", color="info", variant="filled", size="sm", radius="sm", icon=True, key="alert_2")

            if plot_choose == '共享服务统计图':

                if not filtered_share.empty:
                    st.markdown('<div style="text-align: center; font-weight: bold; font-size: 20px;">共享服务统计图</div>', unsafe_allow_html=True)
                    st.write("")
                    filtered_share['日期'] = filtered_share['日期'].astype(str)
                    summary = filtered_share.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
                else:
                    st.write("")
                    sac.alert("**暂无此项统计数据，快去使用吧！**", color="info", variant="filled", size="lg", radius="sm", icon=True, key="alert_3")

            if plot_choose == '注册人数统计图':
                if not filtered_sign.empty:
                    st.markdown('<div style="text-align: center; font-weight: bold; font-size: 20px;">注册人数统计图</div>', unsafe_allow_html=True)
                    st.write("")
                    filtered_sign['日期'] = filtered_sign['日期'].astype(str)
                    summary = filtered_sign.groupby(['日期', 'user']).size().reset_index(name='注册总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='注册总计').fillna(0)
                    st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
                else:
                    st.write("")
                    sac.alert("**暂无此项统计数据，快去使用吧！**", color="info", variant="filled", size="lg", radius="sm", icon=True, key="alert_4")

            if plot_choose == '时段人数统计图':
                if not filtered_user.empty:
                    st.markdown('<div style="text-align: center; font-weight: bold; font-size: 20px;">时段人数统计图</div>', unsafe_allow_html=True)
                    st.write("")
                    data = filtered_user.copy()
                    data['小时'] = pd.to_datetime(data['日期时间']).dt.hour
                    data['时段'] = data['小时'].apply(lambda hour: (
                        '00:00-04:00' if 0 <= hour < 4 else
                        '04:00-08:00' if 4 <= hour < 8 else
                        '08:00-12:00' if 8 <= hour < 12 else
                        '12:00-16:00' if 12 <= hour < 16 else
                        '16:00-20:00' if 16 <= hour < 20 else
                        '20:00-24:00'
                    ))
                    summary = data.groupby(['日期', '时段']).size().reset_index(name='登录总计')
                    summary['日期'] = pd.to_datetime(summary['日期']).dt.date
                    chart = alt.Chart(summary).mark_bar().encode(
                        x=alt.X('日期:T', title='日期', timeUnit='yearmonthdate'),
                        y=alt.Y('时段:N', title='时段'),
                        color='登录总计:Q',
                        tooltip=['日期', '时段', '登录总计']
                    ).properties(
                        height=height,
                        width=800
                    ).configure_axis(
                        labelAngle=15
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.write("")
                    sac.alert("**暂无此项统计数据，快去使用吧！**", color="info", variant="filled", size="lg", radius="sm", icon=True, key="alert_5")

            st.divider()
            st.write("**运行日志**")
            lines.reverse()
            result_str = "".join(str(line) for line in lines)
            st.text_area("运行日志", value=result_str, height=300, label_visibility="collapsed")
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                if st.button("**清理日志**", use_container_width=True, type=button_type):
                    log_content = "【OaiT服务已成功开启！】\n"
                    with open(current_path + "/app.log", "w", encoding="utf-8") as log_file:
                        log_file.write(log_content)
                    st.rerun()
            st.write("")

    if set_choose == '基本设置':
        if not web_setting["web"]["readme"]:
            readme()

        with st.container(border=True):
            st.write("**网站设置**")

            col1, col2 = st.columns(2)
            with col1:
                super_user = st.text_input("**管理员昵称**", value=web_setting["web"]["super_user"])
                super_key = st.text_input("**管理员密钥**", value=web_setting["web"]["super_key"], type="password")
            with col2:
                title = st.text_input("**站点标题**", value=web_setting["web"]["title"])
                subtitle = st.text_input("**站点副标题**", value=web_setting["web"]["subtitle"])

            col1, col2 = st.columns(2)
            with col1:
                login_theme = st.selectbox("**主题**", ["free", "classic"], index=["free", "classic"].index(web_setting["web"]["login_Theme"]))
            with col2:
                button_style = st.selectbox("**按钮样式**", ["Classic-black", "Simple-white", "Primary", "Secondary"], index=["Classic-black", "Simple-white", "Primary", "Secondary"].index(web_setting["web"]["button_style"]))

            if button_style not in ["Primary", "Secondary"]:
                col1, col2 = st.columns(2)
                with col1:
                    button_border = st.selectbox("**按钮边框**", ["#000", "#111", "#222", "#333", "#444", "#666", "#888", "#AAA", "#CCC", "#FFF"], index=["#000", "#111", "#222", "#333", "#444", "#666", "#888", "#AAA", "#CCC", "#FFF"].index(web_setting["web"]["button_border"]))
                with col2:
                    button_border_radius = st.number_input("**按钮圆角**", value=web_setting["web"]["button_border_radius"], min_value=0, max_value=50, step=1)

            st.write("")
            col6, col7, col8 = st.columns([0.2, 0.2, 0.6])
            col1, col2 = st.columns([0.99999, 0.00001])
            with col6:
                if st.button("**保存更改**", use_container_width=True, key="save_setting_web", type=button_type):
                    if super_key == "" or super_user == "":
                        st.toast("**管理员昵称和密钥不能为空！**", icon=':material/error:')
                    elif len(super_key) < 8:
                        st.toast("**管理员密钥长度不能小于8位！**", icon=':material/error:')
                    else:
                        web_setting["web"]["login_Theme"] = login_theme
                        web_setting["web"]["button_style"] = button_style
                        web_setting["web"]["super_user"] = super_user
                        web_setting["web"]["super_key"] = super_key
                        web_setting["web"]["title"] = title
                        web_setting["web"]["subtitle"] = subtitle
                        if button_style not in ["Primary", "Secondary"]:
                            web_setting["web"]["button_border"] = button_border
                            web_setting["web"]["button_border_radius"] = button_border_radius

                        with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                            toml.dump(web_setting, f)
                        logger.info(f"<管理员> 【基本设置】 更新了网站基本设置！")
                        st.rerun()

            st.divider()
            st.write("**服务域名**")
            sac.alert(label="**类型中 `Newest` 指向 最新UI， `Classic` 指向 Pandora 经典UI**", color="info", variant='quote', size="lg", radius="sm", icon=True)
            rows = [[datas['name'], name, datas['speed'], datas['type']]
                    for name, datas in domain_data.items()]
            df0 = pd.DataFrame(rows, columns=["命名", "服务域名", "延迟", "类型"])

            col1, col2 = st.columns(2)
            try:
                with col1:
                    choose_domain = st.selectbox("**是否允许用户选择域名**", ["允许", "不允许"], index=["允许", "不允许"].index(web_setting["web"]["choose_domain"]))
            except:
                with col1:
                    choose_domain = st.selectbox("**是否允许用户选择域名**", ["允许", "不允许"], index=1)
            try:
                with col2:
                    if choose_domain == "不允许":
                        domain = st.selectbox("**默认服务域名**", df0["服务域名"].tolist(), index=df0["服务域名"].tolist().index(web_setting["web"]["domain"]))
                    else:
                        user_domain = st.multiselect("**允许用户使用的域名**", df0["服务域名"].tolist(), default=web_setting["web"]["user_domain"])
            except:
                with col2:
                    if choose_domain == "不允许":
                        domain = st.selectbox("**默认服务域名**", df0["服务域名"].tolist())
                    else:
                        user_domain = st.multiselect("**允许用户选择的域名**", df0["服务域名"].tolist())
            data = st.data_editor(df0, hide_index=True, use_container_width=True, height=143, num_rows="dynamic", disabled=["延迟"], column_config={"类型": st.column_config.SelectboxColumn(options=["Newest", "Classic"])})

            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                if st.button("**保存更改**", use_container_width=True, key="save_domain", type=button_type):
                    if len(user_domain) == 0:
                        st.toast("**允许用户使用的域名不能为空！**", icon=':material/error:')
                    else:
                        web_setting["web"]["choose_domain"] = choose_domain
                        if choose_domain == "不允许":
                            web_setting["web"]["domain"] = domain
                        else:

                            web_setting["web"]["user_domain"] = user_domain
                        json_data = data.to_dict('records')
                        json_data = {str(record['服务域名']): {
                            'name': record['命名'],
                            'speed': record['延迟'],
                            'type': record['类型']
                        } for record in json_data}
                        json.dumps(json_data, indent=2)
                        with open(current_path + "domain.json", "w", encoding="utf-8") as f:
                            json.dump(json_data, f, indent=2)
                        logger.info(f"<管理员> 【域名设置】 更新了域名服务设置！")
                        st.toast("**更改成功!**", icon=':material/check_circle:')
                        with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                            toml.dump(web_setting, f)
            with col7:
                if st.button("**测试延迟**", use_container_width=True, type=button_type):
                    delay = []
                    for i in rows:
                        try:
                            start_time = time.time()
                            response = requests.get("https://" + i[1])
                            end_time = time.time()
                            total_time = end_time - start_time
                            delay.append(str(round(total_time, 2)) + "s")
                        except:
                            delay.append("无法连接")
                    json_data = {}
                    for i, record in zip(delay, data.to_dict('records')):
                        json_data[record['服务域名']] = {
                            'name': record['命名'],
                            'speed': i,
                            'type': record['类型']
                        }
                    with open(current_path + "domain.json", "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=2)
                    st.rerun()

            st.divider()
            st.write("**公告设置**")
            col1, col2 = st.columns(2)
            with col1:
                notice_enable = st.checkbox("**开启站点公告**", value=web_setting["web"]["notice_enable"])
                notice_title = st.text_area("**站点公告-主标题(支持markdown)**", value=web_setting["web"]["notice_title"], height=122)
                notice_subtitle = st.text_area("**站点公告-次标题(支持markdown)**", value=web_setting["web"]["notice_subtitle"], height=122)
            with col2:
                style = ['light', 'filled', 'outline', 'transparent', 'quote', 'quote-light']
                color = ['success', 'info', 'warning', 'error', 'dark', 'gray', 'red', 'pink', 'grape', 'violet', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange']
                size = ['xs', 'sm', 'md', 'lg', 'xl']
                notice_banner = st.checkbox("**公告滚动效果**", value=web_setting["web"]["notice_banner"])
                notice_size = st.selectbox("**公告大小**", size, index=size.index(web_setting["web"]["notice_size"]))
                notice_radius = st.selectbox("**公告圆角**", size, index=size.index(web_setting["web"]["notice_radius"]))
                notice_style = st.selectbox("**公告样式**", style, index=style.index(web_setting["web"]["notice_style"]))
                notice_color = st.selectbox("**公告颜色**", color, index=color.index(web_setting["web"]["notice_color"]))

            col6, col7, col8 = st.columns([0.2, 0.2, 0.6])
            with col6:
                if st.button("**保存更改**", use_container_width=True, key="save_notice", type=button_type):
                    web_setting["web"]["notice_enable"] = notice_enable
                    web_setting["web"]["notice_enable"] = notice_enable
                    web_setting["web"]["notice_banner"] = notice_banner
                    web_setting["web"]["notice_size"] = notice_size
                    web_setting["web"]["notice_radius"] = notice_radius
                    web_setting["web"]["notice_style"] = notice_style
                    web_setting["web"]["notice_title"] = notice_title
                    web_setting["web"]["notice_color"] = notice_color
                    web_setting["web"]["notice_subtitle"] = notice_subtitle
                    with open(current_path + "/setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    logger.info(f"<管理员> 【公告设置】 更新了站点公告！")
                    st.toast("**更改成功!**", icon=':material/check_circle:')

            st.write("")
            st.write("")
            col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
            with col3:
                st.write("")
                st.write("")
                st.write("##### 公告样式预览")
            with col2:
                sac.alert(label=notice_title, description=notice_subtitle, color=notice_color, banner=notice_banner, variant=notice_style, size=notice_size, radius=notice_radius)
            st.write("")
            st.write("")

    if set_choose == '号池管理':
        with st.container(border=True):
            st.write("**号池列表**")
            sac.alert(label="**用户组 是每个账号的唯一标识，不允许命名相同**", description="**用户组是各个模块相互联系的重要关键字，命名后请谨慎二次修改**", color="info", variant='quote', size="lg", radius="lg", icon=True, closable=True)

            fields = ['用户组', '订阅类型', '账户邮箱', 'AC_Token', 'RF_Token']
            rows = [[groups, datas['account_type'], datas['account'], datas['access_token'], datas['refresh_token']] for groups, datas in accounts.items()]
            df1 = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_account"]), key="hide_index_account")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_account"], min_value=100, max_value=1000, step=100, key="height_account")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_account"]), key="order_what_account")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index(web_setting["excel"]["order_row_account"]), key="order_row_account")

                order = st.multiselect("**数据显示**", fields, web_setting["excel"]["order_account"], key="order_account")
                if order_row == "升序":
                    df1 = df1.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df1 = df1.sort_values(by=order_what, ascending=False)

            edited_df1 = st.data_editor(df1, hide_index=hide_index, use_container_width=True, num_rows="dynamic", height=height, column_config={"订阅类型": st.column_config.SelectboxColumn(options=["Free", "Plus"])}, column_order=order)
            col6, col7, col8, col9 = st.columns([0.2, 0.2, 0.2, 0.4])
            with col6:
                if st.button("**保存更改**", use_container_width=True, type=button_type):
                    web_setting["excel"]["hide_index_account"] = hide_index
                    web_setting["excel"]["height_account"] = height
                    web_setting["excel"]["order_what_account"] = order_what
                    web_setting["excel"]["order_row_account"] = order_row
                    web_setting["excel"]["order_account"] = order
                    json_data1 = df_to_json1(edited_df1)
                    json_filename = 'accounts.json'

                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    with open(current_path + json_filename, 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data1)

                    logger.info(f"<管理员> 【账户更改】 更新了账户信息！")
                    st.toast("**更改成功!**", icon=':material/check_circle:')
            with col7:
                if st.button("**新增账户**", use_container_width=True, type=button_type):
                    new_account()
            with col8:
                st.link_button("**获取RF令牌**", "https://token.oaifree.com/auth", use_container_width=True, type=button_type)

            st.divider()
            st.write("**邀请令牌**")
            sac.alert(label="**您必须重新设置 至少一个邀请令牌，允许多个邀请令牌对应同一用户组。**", variant='quote', color="info", size="lg", radius="lg", icon=True, closable=True)

            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                invite_link_enable = st.checkbox("**显示发卡平台链接**", value=web_setting["web"]["invite_link_enable"], key="invite_link_enable")
            with col2:
                if invite_link_enable:
                    invite_link = st.text_input("**发卡链接**", value=web_setting["web"]["invite_link"], key="invite_link", label_visibility="collapsed")

            fields = ['Invite_Token', '用户组', '备注', '是否使用']
            rows = [[IV_Token, invite_config[IV_Token]["group"], invite_config[IV_Token]["note"], invite_config[IV_Token]["used"]] for IV_Token, Group in invite_config.items()]
            df3 = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_invite"]), key="hide_index_invite")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_invite"], min_value=100, max_value=1000, step=100, key="height_invite")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_invite"]), key="order_what")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index(web_setting["excel"]["order_row_invite"]), key="order_row")

                col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
                with col1:
                    order = st.multiselect("**数据显示**", fields, web_setting["excel"]["order_invite"], key="order", label_visibility="collapsed")
                with col2:
                    if st.button("**删除已用令牌**", use_container_width=True, key="delete_invite", type=button_type):
                        for i in list(invite_config.keys()):
                            if invite_config[i]["used"]:
                                invite_config.pop(i)
                        with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                            json.dump(invite_config, f, indent=2)
                        st.toast("**删除成功!**", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【邀请令牌】 删除了已使用的邀请令牌！")
                        st.rerun()
                with col3:
                    if st.button("**删除所有令牌**", use_container_width=True, key="delete_all_invite", type=button_type):
                        invite_config.clear()
                        with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                            json.dump(invite_config, f, indent=2)
                        st.toast("**删除成功!**", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【邀请令牌】 删除了所有的邀请令牌！")
                        st.rerun()

                if order_row == "升序":
                    df3 = df3.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df3 = df3.sort_values(by=order_what, ascending=False)

            edited_df3 = st.data_editor(df3, hide_index=hide_index, use_container_width=True, height=height, column_order=order, num_rows="dynamic", column_config={"group": st.column_config.SelectboxColumn(options=accounts.keys())}, disabled=["是否使用"])
            col1, col2, col3, col4 = st.columns([0.2, 0.2, 0.2, 0.4])
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_invite", type=button_type):
                    web_setting["excel"]["hide_index_invite"] = hide_index
                    web_setting["excel"]["height_invite"] = height
                    web_setting["excel"]["order_what_invite"] = order_what
                    web_setting["excel"]["order_row_invite"] = order_row
                    web_setting["excel"]["order_invite"] = order
                    web_setting["web"]["invite_link_enable"] = invite_link_enable
                    if invite_link_enable:
                        web_setting["web"]["invite_link"] = invite_link
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)

                    dict_for_check, json_data3 = df_to_json3(edited_df3)
                    json_filename = 'invite.json'
                    success = 0
                    for a, b in dict_for_check.items():
                        if a is not None and b is not None and a != 'None' and b != 'None' and a != '' and b != '':
                            success = 1
                        else:
                            success = 0
                    if json_data3 != "{}" and success:
                        with open(current_path + json_filename, 'w', encoding='utf-8') as json_file:
                            json_file.write(json_data3)
                        st.toast("**更改成功!**", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【邀请令牌更改】 更新了邀请令牌信息！")
                    else:
                        with col6:
                            sac.alert(label="**保存失败，您必须设置至少一个邀请令牌，并设置正确的用户组，不允许为空值!**", color="error", variant='filled', size="md", radius="sm", icon=True)
            with col2:
                if st.button("**生成令牌**", use_container_width=True, key="new_invite_token", type=button_type):
                    new_invite()
            with col3:
                if st.button("**新用户权限**", use_container_width=True, type=button_type):
                    invite()

            st.divider()
            st.write("**AC 刷新**")
            sac.alert(
                label="**开启后登陆时会自动检测用户的SA_Token，当状态获取失败则会自动尝试刷新SA_Token和AC_Token，实现用户状态刷新自动化**",
                description="**已对有时间限制的用户（expires_in不为0）进行单独优化，开启后 不会重置此类用户的剩余时间**",
                color="info", variant='quote', size="lg", radius="lg", icon=True, closable=True)
            refresh = st.checkbox("**开启 SA/AC 自动检测刷新**", value=web_setting["web"]["refresh_all"])

            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_AC_Token刷新", type=button_type):
                    web_setting["web"]["refresh_all"] = refresh
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)

            st.divider()
            st.write("**AC 刷新 (手动)**")
            group = st.selectbox("**选择需要刷新用户组**", accounts.keys())
            col1, col2 = st.columns([0.2, 0.8])
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button(f"**刷新 - {group}**", use_container_width=True, type=button_type):
                    status, new_access_token = get_accesstoken(accounts[group]['refresh_token'])
                    if status:
                        st.toast(f"**刷新 {group} 成功！**", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【AC刷新】 刷新了 {group} 组的 AC_Token！")
                        accounts[group]['access_token'] = new_access_token
                        with open(current_path + "accounts.json", "w", encoding="utf-8") as f:
                            json.dump(accounts, f, indent=2)
                    else:
                        with col6:
                            logger.error(f"<管理员> 【AC刷新】 刷新 {group} 组的 AC_Token 失败！")
                            sac.alert(label="**AC_Token 刷新失败！请检查您的RF_Token是否已过期！**", color="error", variant='filled', size="md", radius="sm", icon=True)

    if set_choose == '用户管理':
        with st.container(border=True):
            st.write("**用户列表**")
            sac.alert(label="**所有表格均支持 `搜索`、`下载`、`新建`、`删除`、`修改`、`排序` ，但请务必在修改后进行保存！**", color="info", variant='quote', size="lg", radius="sm", icon=True, closable=True)

            fields = ['账户', '密码', 'UID', 'SA_Token', '用户组', '订阅类型', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离']
            rows = [[user] + list(account.values()) for user, account in config.items()]
            df2 = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_user"]), key="hide_index_user")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_user"], min_value=100, max_value=1000, step=100, key="height_user")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_user"]), key="order_what_user")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index(web_setting["excel"]["order_row_user"]), key="order_row_user")

                order = st.multiselect("**数据显示**", fields, web_setting["excel"]["order_user"], key="order_user")

                if order_row == "升序":
                    df2 = df2.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df2 = df2.sort_values(by=order_what, ascending=False)

            edited_df2 = st.data_editor(df2, column_order=order, hide_index=hide_index, use_container_width=True, height=height, disabled=['用户组', 'UID', '订阅类型', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离'], num_rows="dynamic")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存更改** ", use_container_width=True, key="save_user", type=button_type):
                    web_setting["excel"]["hide_index_user"] = hide_index
                    web_setting["excel"]["height_user"] = height
                    web_setting["excel"]["order_what_user"] = order_what
                    web_setting["excel"]["order_row_user"] = order_row
                    web_setting["excel"]["order_user"] = order
                    with open(current_path + '/setting.toml', 'w', encoding='utf-8') as f:
                        toml.dump(web_setting, f)
                    json_data2 = df_to_json2(edited_df2)
                    with open(current_path + '/config.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data2)
                    st.toast("**更改成功！**", icon=':material/check_circle:')
                    logger.info(f"<管理员> 【用户更改】 更新了用户信息！")
            with col2:
                if st.button("**状态刷新**", use_container_width=True, type=button_type):
                    refresh_user()
            with col3:
                st.link_button("**获取 SA 令牌**", "https://chat.oaifree.com/token", use_container_width=True, type=button_type)

            st.divider()
            st.write("**刷新令牌**")
            sac.alert(label="**开启后允许被限制时间的用户在首页的 `无法登录？`内续费，您可设置不同类型的令牌来设置用户的续费时间**", description="**最多 10 天，升级永久请将令牌的过期秒数设置为 0**", color="info", variant='quote', size="lg", radius="lg", icon=True, closable=True)
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                user_refresh = st.checkbox("**开启续费功能**", value=web_setting["web"]["user_refresh"])
            with col2:
                refresh_link_enable = st.checkbox("**显示发卡平台链接**", value=web_setting["web"]["refresh_link_enable"], key="refresh_link_enable")
            with col3:
                if refresh_link_enable:
                    refresh_link = st.text_input("**发卡链接(完整网址)**", value=web_setting["web"]["refresh_link"], key="refresh_link", label_visibility="collapsed")

            fields = ['userRF_Token', '用户组', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离', '备注', '是否使用']
            rows = [[rf_token] + list(datas.values()) for rf_token, datas in refresh_data.items()]
            df4 = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_refresh"]), key="hide_index_refresh")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_refresh"], min_value=100, max_value=1000, step=100, key="height_refresh")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_refresh"]), key="order_what_refresh")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index(web_setting["excel"]["order_row_refresh"]), key="order_row_refresh")

                col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
                with col1:
                    order = st.multiselect("**数据显示**", fields, web_setting["excel"]["order_refresh"], key="order_refresh", label_visibility="collapsed")
                with col2:
                    if st.button("**删除已用令牌**", use_container_width=True, key="delete_refresh", type=button_type):
                        for i in list(refresh_data.keys()):
                            if refresh_data[i]["used"]:
                                refresh_data.pop(i)
                        with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                            json.dump(refresh_data, f, indent=2)
                        st.toast("**删除成功!**", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【刷新令牌】 删除了已使用的刷新令牌！")
                        st.rerun()
                with col3:
                    if st.button("**删除所有令牌**", use_container_width=True, key="delete_all_refresh", type=button_type):
                        refresh_data.clear()
                        with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                            json.dump(refresh_data, f, indent=2)
                        st.toast("**删除成功!**", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【刷新令牌】 删除了所有刷新令牌！")
                        st.rerun()

                if order_row == "升序":
                    df4 = df4.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df4 = df4.sort_values(by=order_what, ascending=False)

            edited_df4 = st.data_editor(df4, hide_index=hide_index, use_container_width=True, height=height, num_rows="dynamic", disabled=["是否使用"], column_order=order, column_config={"用户组": st.column_config.SelectboxColumn(options=accounts.keys())})
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_refresh", type=button_type):
                    web_setting["web"]["user_refresh"] = user_refresh
                    web_setting["web"]["refresh_link_enable"] = refresh_link_enable
                    if refresh_link_enable:
                        web_setting["web"]["refresh_link"] = refresh_link
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    json_data4 = df_to_json4(edited_df4)
                    with open(current_path + 'refresh.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data4)
                    st.toast("**更改成功！**", icon=':material/check_circle:')
                    logger.info(f"<管理员> 【刷新令牌】 更新了刷新令牌信息！")
            with col2:
                if st.button("**生成令牌**", use_container_width=True, key="new_refresh_token", type=button_type):
                    new_refresh()

            st.divider()
            st.write("**用户注册 - 管理员**")
            sac.alert(label="**`限制网站`为空时无限制；`过期秒数` 为0时永不过期；`GPT3.5限制` 为-1时无限制；`GPT4限制` 为-1时无限制；`会话无需隔离` 为true时不隔离会话**", color="info", variant='quote', size="lg", radius="lg", icon=True)
            col1, col2 = st.columns(2)
            with col1:
                user_new_acc = st.text_input("**账户**", key="user_new_acc_admin", placeholder="user_name")
                user_new_pass = st.text_input("**密码**", key="user_new_pass_admin", type="password", placeholder="user_password")
                user_new_group = st.selectbox("**组别**", accounts.keys())
                show_conversations = st.selectbox("**会话无需隔离**", ['true', 'false'], index=1, help="false为隔离会话")
            with col2:
                site_limit = st.text_input("**限制网站（为空不限制）**", value="", help="限制的网站, 为空则不限制", placeholder="site1,site2")
                expires_in = st.number_input("**有效期（秒**）", value=0, help="token有效期（单位为秒），填 0 则永久有效")
                gpt35_limit = st.number_input("**限制GPT-3.5**", value=-1, help="GPT-3.5对话限制，填 -1 则不限制")
                gpt4_limit = st.number_input("**限制GPT-4**", value=-1, help="GPT-4对话限制，填 -1 则不限制")
            uid = st.text_input("**UID(32位)**", value="UID-" + secrets.token_urlsafe(32), help="用户的UID，自动生成，用于用户登录、修改密码", disabled=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**注册用户**", use_container_width=True, key="register_user_admin", type=button_type):
                    if user_new_acc == "":
                        with col6:
                            sac.alert(label="**请先填写账户昵称!**", color="error", variant='filled', size="lg", radius="sm", icon=True)
                    elif user_new_pass == "":
                        with col6:
                            sac.alert(label="**请填写账户密码!**", color="error", variant='filled', size="lg", radius="sm", icon=True)
                    elif user_new_acc in config:
                        with col6:
                            sac.alert(label="**该账户已存在，请修改!**", color="error", variant='filled', size="md", radius="sm", icon=True)
                    else:
                        group_data = accounts[user_new_group]
                        acc = group_data['access_token']
                        status, new_name, new_token_key = get_sharetoken(user_new_acc, acc, site_limit, expires_in, gpt35_limit, gpt4_limit, show_conversations)
                        if status:
                            json_data = {
                                new_name: {
                                    'password': user_new_pass,
                                    'uid': uid,
                                    'token': new_token_key,
                                    'group': user_new_group,
                                    'type': group_data['account_type'],
                                    'site_limit': site_limit,
                                    'expires_in': expires_in,
                                    'gpt35_limit': gpt35_limit,
                                    'gpt4_limit': gpt4_limit,
                                    'show_conversations': show_conversations,
                                }
                            }

                            config.update(json_data)
                            config_json = json.dumps(config, indent=2)
                            json_filename = 'config.json'
                            with open(current_path + json_filename, 'w', encoding='utf-8') as json_file:
                                json_file.write(config_json)
                            st.toast("**注册成功！**", icon=':material/check_circle:')
                            st.toast("**即将刷新页面...1s**", icon=':material/check_circle:')
                            time.sleep(1)
                            logger.info(f"<管理员> 【用户注册】 新用户注册成功！uid：{uid}，name：{new_name}，token:{new_token_key}，group:{user_new_group}")
                            st.rerun()
                        else:
                            with col6:
                                sac.alert(label="**注册失败，请检查 AC_Token 状态！**", color="error", variant='filled', size="lg", radius="sm", icon=True)
            with col2:
                if st.button("**前往首页**", use_container_width=True, key="go_home", type=button_type):
                    st.switch_page("home.py")

    if set_choose == '更多功能':
        with st.container(border=True):
            st.write('')
            st.write("**Share 共享站**")
            share = st.checkbox("**开启Share功能（免费试用）**", value=web_setting["web"]["share"])
            if share:
                share_notice = st.text_area("**Share站公告** (支持MarkDown)", value=web_setting["web"]["share_notice"])
                share_list = share_data.keys()
                index = []
                for i in share_list:
                    index.append(list(config.keys()).index(i))
                share_account = sac.transfer(items=config.keys(), index=index, titles=['用户池', '共享池'], use_container_width=True, reload=True, align='center', search=True, pagination=True, width=500, height=400, color="dark")

            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存更改**", use_container_width=True, type=button_type, key="save_share_setting"):
                    web_setting["web"]["share"] = share
                    if share:
                        web_setting["web"]["share_notice"] = share_notice
                        if share_account is None:
                            share_data = {}
                            with open(current_path + "share.json", "w") as share_file:
                                json.dump(share_data, share_file, indent=2)
                            st.toast("保存成功！", icon=":material/check_circle:")
                        else:
                            share_data = {key: config[key] for key in share_account if key in config}
                            with open(current_path + "share.json", "w") as share_file:
                                json.dump(share_data, share_file, indent=2)
                            st.toast("保存成功！", icon=":material/check_circle:")
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    logger.info(f"<管理员> 【Share设置】 更新了Share设置！")
            with col2:
                if st.button("**前往Share站**", use_container_width=True, type=button_type):
                    st.switch_page("pages/share.py")

            st.divider()
            st.write("**关于**")
            st.write(f"版本：OaiT {version}")
            st.write("作者：@Chenyme")
            st.write("鸣谢：@Neo")
            st.write("GitHub：https://github.com/Chenyme/oaifree-tools")
            st.write("有任何问题欢迎提 issue，如果觉得好用请给我一个 Star 吧，感谢支持！")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**更多**", use_container_width=True, type=button_type):
                    readme()

            st.divider()
            st.write("**友情链接**")
            st.write("下面是 Neo博客站、Linux论坛、项目框架、个人其他项目的链接，欢迎访问！")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.link_button("**我的 GitHub**", "https://github.com/Chenyme", use_container_width=True, type=button_type)
            with col2:
                st.link_button("**Linux 论坛**", "https://linux.do", use_container_width=True, type=button_type)
            with col3:
                st.link_button("**zhile 博客**", "https://zhile.io/", use_container_width=True, type=button_type)
            with col4:
                st.link_button("**Streamlit**", "https://streamlit.io", use_container_width=True, type=button_type)
            with col5:
                st.link_button("**全自动视频翻译**", "https://github.com/Chenyme/Chenyme-AAVT", use_container_width=True, type=button_type)

    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center;">
            <img src="data:image/png;base64,{encoded_image}" alt="LOGO" style="width: 200px;">
            <p style="text-align: center; color: gray; font-size: 12px; margin-top: -40px;">一键管理Oaifree服务，简单上手</p>
            <p style="text-align: center; color: gray; font-size: 12px; margin-top: -20px;">OaiT {version}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    col1, col2, col3 = st.columns(3)
    with col2:
        sac.alert("**非法访问！**", "**警告：你无权进入该页面！**", color="error", size="lg", radius="lg", icon=True,
                  variant="filled", closable=True)
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
            admin = st.text_input("**管理账户：**")
            key = st.text_input("**管理密钥：**", type="password")
            st.divider()
            if st.button("**验证身份**", use_container_width=True, type=button_type):
                if admin == web_setting["web"]["super_user"] and key == web_setting["web"]["super_key"]:
                    st.session_state.role = "admin"
                    st.write("")
                    st.switch_page("pages/admin.py")
                else:
                    st.toast("**身份验证失败，如果您不是管理员请前往首页进行登录！**", icon=":material/error:")
            st.write("")
            st.page_link("home.py", label="**:blue[返回首页登录]**")
            st.write("")

st.markdown(footer, unsafe_allow_html=True)  # 底部信息,魔改请勿删除