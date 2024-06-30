import os
import re
import time
import json
import toml
import math
import secrets
import logging
import zipfile
import requests
from io import BytesIO
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
from utils import get_accesstoken, get_sharetoken, df_to_json1, df_to_json2, df_to_json3, df_to_json4, check_sharetoken

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

st.set_page_config(layout="wide", page_title=web_setting["web"]["title"], page_icon="LOGO.png")

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


# 阻止非法访问
if "role" not in st.session_state:
    st.session_state.role = None
if st.session_state.role == "admin":

    @st.experimental_dialog("安全保护")
    def key():
        col1, col2, col3 = st.columns([0.42, 0.26, 0.42])
        with col2:
            st.image("LOGO.png", width=200, caption="安全保护", use_column_width=True)
        st.write("")
        super_user = st.text_input("**新的昵称**", value=web_setting["web"]["super_user"])
        super_key = st.text_input("**新的密钥**", value=web_setting["web"]["super_key"])
        st.write("")
        sac.alert(label='**首次登入请修改super_key(管理员密钥)**', color="warning", size='md', radius='lg', icon=True,
                  closable=True)
        st.write("")
        if st.button("**保存更改**", use_container_width=True, type="primary"):
            if len(super_key) < 8:
                st.write("")
                st.error("密码需大于等于8位，请重新输入！", icon=":material/error:")
            elif super_key == "12345678":
                st.write("")
                st.error("密码与原密码相同，请重新输入！", icon=":material/error:")
            else:
                web_setting["web"]["super_user"] = super_user
                web_setting["web"]["super_key"] = super_key
                st.success("修改成功!", icon=":material/check_circle:")
                time.sleep(1)
                with open(current_path + "/setting.toml", "w", encoding="utf-8") as f:
                    toml.dump(web_setting, f)
                logger.info(f"<管理员> 【密钥修改】 修改了新的密钥！")
                st.rerun()
        st.write("")

    @st.experimental_dialog("使用说明")
    def readme():
        col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
        with col2:
            st.image("LOGO.png", width=50, use_column_width=True)
        st.markdown("""
            - **制作不易，不许白嫖，请给一颗免费的心叭！开源项目可魔改，但请务必保留原作者信息、遵循开源协议。**
            
            - **OAIFree的管理后台，提供大量管理功能，包括：**
            
                - **站点工具**：登录统计、运行日志、站点迁移。
                - **账户管理**：管理号池、管理用户、管理权限。
                - **个性化设置**：修改站点标题、站点副标题、站点公告。
                - **多域名管理**：负载分流、支持新老UI。
                - **TOKEN刷新**：自动刷新SA_Token、AC_Token。
                - **Share共享**：共享账户登录。
                - **邀请令牌**：可用于自动化管理新用户注册。
                - **刷新令牌**：可用于自动化续费账户状态。
            
            ---
            
            - **注意事项：**
                
                - **请勿随意上传错误的配置文件，否则可能导致程序无法正常运行。**
                - **设置时务必及时保存修改，每个模块均有保存按钮，否则不会生效。**
                - **新增号池用户组时，请务必保证用户组的名称不重复，因为用户组是账号的唯一标识。**
                - **当你修改任意表格时，请修改后点击空白处，否则有可能保存失败。（可能会发生）**
                - **登陆时若出现 Press Enter To Apply，请及时按回车或点击页面空白处，否则有可能登录失败。（可能会发生）**
            
            ---
            
            - **特别鸣谢：**
            
                - **感谢 Neo 大佬，为我们提供了这么好用的服务。**
                - **我们饱受OpenAI的区别对待，真的非常始皇（Neo）的辛勤付出！让我们能够无差别使用GPT的服务。**
                - **我是Chenyme，期待我们的下次相遇！**
            # OpenAI，Not CloseAI！愿开源精神永存！
                
            ---

        """)

        if st.button("**我已知晓，不再弹出**", use_container_width=True):
            web_setting["web"]["readme"] = True
            with open(current_path + "/setting.toml", "w", encoding="utf-8") as f:
                toml.dump(web_setting, f)
            st.rerun()
        st.link_button("**来GitHub给我一颗星叭！**", "https://github.com/Chenyme/oaifree-tools", use_container_width=True)

    @st.experimental_dialog("新增账户")
    def new_account():
        col1, col2 = st.columns(2)
        with col1:
            new_group = st.text_input("**新的用户组昵称***", value="")
        with col2:
            new_account_type = st.selectbox("**订阅套餐***", ["Free", "Plus"], index=1, help="订阅套餐情况，不可为空")
        new_account = st.text_input("**账户邮箱**", value="", help="账户邮箱，用于标识备注，可为空")
        new_access_token = st.text_input("**AC_Token***", help="AC_Token，登录的必要Token，不可为空")
        new_refresh_token = st.text_input("**RF_Token**", help="RF_Token，用于AC刷新的Token，可为空，为空则刷新功能不可用")
        st.write("")
        if st.button("**保存新账户**", use_container_width=True, type="primary"):
            if new_group in accounts.keys():
                sac.alert(label="该用户组已存在，请重新命名！", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
            elif new_group == "":
                sac.alert(label="用户组不能为空，请重新命名！", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
            elif new_access_token == "":
                sac.alert(label="AC_Token不能为空，请重新填写！", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
            elif new_refresh_token == "":
                sac.alert(label="RF_Token不能为空，请重新填写！", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
            else:
                accounts[new_group] = {
                    "account_type": new_account_type,
                    "account": new_account,
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                }
                with open(current_path + "accounts.json", "w", encoding="utf-8") as f:
                    json.dump(accounts, f, indent=2)
                logger.info(f"<管理员> 【账户新增】 新增用户组:{new_group}，账户订阅:{new_account_type}，账户邮箱:{new_account}")
                sac.alert(label="保存成功！", color="success", variant='quote', size="md", radius="lg", icon=True, closable=True)
                time.sleep(1)
                st.rerun()

    @st.experimental_dialog("站点迁移-配置导出")
    def download():
        st.write("")
        st.write("**请选择需要导出的配置文件**")
        st.write("")
        files = st.multiselect("选择的文件", ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json", "app.log", "refresh.json", "domain.json"], ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json", "app.log", "refresh.json", "domain.json"], label_visibility="collapsed")
        st.write("")
        if st.button("**导出数据**", use_container_width=True):
            st.write("")
            directory_path = current_path
            zip_buffer = BytesIO()
            try:
                sac.alert(label="准备数据中,请耐心等待...", color="info", variant='quote', size="sm", radius="lg", icon=True, closable=True)
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for root, _, _ in os.walk(directory_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, directory_path)
                            zip_file.write(file_path, arcname)
                zip_buffer.seek(0)
                col1, col2 = st.columns(2)
                i = 1
                for file in files:
                    if i%2 == 0:
                        with col1:
                            sac.alert(label=f"{file}", color="success", variant='quote', size="sm", radius="lg", icon=True, closable=True)
                    if i%2 == 1:
                        with col2:
                            sac.alert(label=f"{file}", color="success", variant='quote', size="sm", radius="lg", icon=True, closable=True)
                    i += 1
                st.write("")
                st.download_button(
                    label="**点击下载**",
                    data=zip_buffer,
                    file_name="config.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
            except:
                sac.alert(label="导出失败！", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
        st.write("")

    @st.experimental_dialog("站点迁移-配置导入")
    def upload():
        st.write("")
        st.write("**请上传配置文件**")
        sac.alert(label="**仅支持V1.1.2版本后的配置文件**", description=" 若为V1.1.1及更低版本，请删除config.zip中的不兼容配置：`setting.toml`、`invite.json`、`config.json` ！ ", banner=True, color="info", variant='filled', size="lg", radius="lg", icon=True, closable=True)
        st.write("")
        uploaded_file = st.file_uploader("上传配置文件", type=['zip'], label_visibility="collapsed")
        st.write("")
        st.write("")
        required_files = ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json", "app.log", "refresh.json", "domain.json"]
        if st.button("**上传并配置**", use_container_width=True, type="primary"):
            if uploaded_file is not None:
                zip_buffer = BytesIO(uploaded_file.getvalue())
                with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                    zip_file_list = zip_ref.namelist()
                    success_files = [file for file in required_files if file in zip_file_list]
                    error_files = [file for file in zip_file_list if file not in required_files]
                    sac.alert(label="上传成功！请稍等片刻，正在配置文件...", color="info", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    col1, col2 = st.columns(2)
                    i = 1
                    for file in success_files:
                        zip_ref.extract(file, current_path)
                        if i % 2 == 0:
                            with col1:
                                sac.alert(label=f"{file}", color="success", variant='quote', size="sm", radius="lg", icon=True, closable=True)
                        if i % 2 == 1:
                            with col2:
                                sac.alert(label=f"{file}", color="success", variant='quote', size="sm", radius="lg", icon=True, closable=True)
                        i += 1

                    for file in error_files:
                        sac.alert(label=f"未知文件 {file}", color="error", variant='quote', size="sm", radius="lg", icon=True, closable=True)
                sac.alert(label="所有文件均成功配置！请及时刷新界面以生效！", banner=True, color="success", variant='filled', size="md", radius="lg", icon=True, closable=True)
            else:
                sac.alert(label="请先上传文件！", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
        st.write("")

    @st.experimental_dialog("配置新用户权限")
    def invite():
        site_limit = st.text_input("限制网站（为空不限制）", value="", help="限制的网站, 为空则不限制")
        expires_in = st.number_input("有效期（秒）", value=0, help="token有效期（单位为秒），填 0 则永久有效")
        gpt35_limit = st.number_input("限制GPT-3.5", value=-1, help="GPT-3.5对话限制，填 -1 则不限制")
        gpt4_limit = st.number_input("限制GPT-4", value=-1, help="GPT-4对话限制，填 -1 则不限制")
        show_conversations = st.selectbox("会话无需隔离", ['true', 'false'], index=1, help="false为隔离会话")
        st.write("")
        if st.button("**保存默认配置**", use_container_width=True, type="primary"):
            web_setting["web"]["site_limit"] = site_limit
            web_setting["web"]["expires_in"] = expires_in
            web_setting["web"]["gpt35_limit"] = gpt35_limit
            web_setting["web"]["gpt4_limit"] = gpt4_limit
            web_setting["web"]["show_conversations"] = show_conversations
            with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                toml.dump(web_setting, f)
            logger.info(f"<管理员> 【邀请码设置】 更新了邀请码的默认设置！")
            sac.alert(label="保存成功！", color="success", variant='quote', size="md", radius="lg", icon=True, closable=True)
        st.write("")

    @st.experimental_dialog("生成邀请令牌")
    def new_invite():
        st.write("")
        it_group = st.selectbox("**选择用户组**", list(accounts.keys()), index=0)
        note = st.text_input("**备注**", value="2024", help="备注信息，可为空")
        auto_it_gen = st.checkbox("**批量生成**")
        if auto_it_gen:
            num_it_gen = st.number_input("**生成数量**", value=5, min_value=1, max_value=100)
            len_it_gen = st.number_input("**邀请令牌长度**", value=16, min_value=16, max_value=32)

        else:
            it_token = st.text_input("**邀请令牌**", value="it-")

        st.write("")
        if st.button("**生成邀请令牌**", use_container_width=True, key="new_invite"):
            if auto_it_gen:
                for i in range(num_it_gen):
                    invite_config["it-" + secrets.token_urlsafe(len_it_gen)] = {
                        "group": it_group,
                        "note": note,
                        "used": False
                    }
                logger.info(f"<管理员> 【邀请令牌】 生成了{num_it_gen}个新的邀请令牌！")
            else:
                invite_config[it_token] = {
                    "group": it_group,
                    "note": note,
                    "used": False
                }
                logger.info(f"<管理员> 【邀请令牌】 生成了新的邀请令牌：{it_token}！")
            with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                json.dump(invite_config, f, indent=2)

            sac.alert(label="生成成功！", color="success", variant='filled', size="md", radius="lg", icon=True, closable=True)
            time.sleep(0.5)
            sac.alert(label="即将自动刷新！", color="success", variant='filled', size="md", radius="lg", icon=True, closable=True)
            time.sleep(1.5)
            st.rerun()
        st.write("")

    @st.experimental_dialog("状态刷新")
    def refresh_user():
        st.write("")
        st.write("**账户状态检测**")
        col1, col2 = st.columns([0.8,0.2])
        with col2:
            if st.checkbox("全选", key="all"):
                default = list(config.keys())
            else:
                default = []
        with col1:
            status_list = st.multiselect("选择需要检测的用户", list(config.keys()), default=default, key="status_list", label_visibility="collapsed")

        st.write("")
        if st.button("**状态检测**", use_container_width=True):
            sc_list = []
            er_list = []
            for user in status_list:
                status = check_sharetoken(config[user]["token"])
                if status:
                    sc_list.append(user)

                else:
                    er_list.append(user)
            st.session_state.sc_list = sc_list
            st.session_state.er_list = er_list

        if "sc_list" in st.session_state and "er_list" in st.session_state:
            if len(st.session_state.er_list) == 0 and len(st.session_state.sc_list) != 0:
                sac.alert("所有账户状态正常！", color="success", variant="quote", size="md", radius="md", icon=True, closable=True)
            else:
                df_result = pd.DataFrame({"成功": pd.Series(st.session_state.sc_list), "失败": pd.Series(st.session_state.er_list)})
                st.data_editor(df_result, hide_index=True, use_container_width=True, height=143)
        else:
            st.session_state.er_list = []
            sac.alert("请先检测！", color="warning", variant="quote", size="md", radius="md", icon=True, closable=True)

        st.divider()
        st.write("**需要刷新的账户**")
        user_group = st.multiselect("选择需要刷新的用户", st.session_state.er_list, key="user_groups", label_visibility="collapsed")
        st.write("")
        if st.button("**刷新状态**", use_container_width=True):
            for user in user_group:
                status, name, token_key = get_sharetoken(user_group, accounts[config[user]["group"]]["access_token"], config[user]["site_limit"], config[user]["expires_in"], config[user]["gpt35_limit"], config[user]["gpt4_limit"], config[user]["show_conversations"])
                if status:
                    config[user]["token"] = token_key
                    with open(current_path + '/config.json', 'w', encoding='utf-8') as file:
                        json.dump(config, file, indent=2)
                    sac.alert(f"{user} 刷新成功！请及时刷新页面！", color="success", variant="quote", size="md", radius="md", icon=True, closable=True)
                    logger.info(f"<管理员> 【账户刷新】 账户：{user} 刷新成功！")
                else:
                    sac.alert(f"{user} 刷新失败！", color="error", variant="quote", size="md", radius="md", icon=True, closable=True)
                    logger.error(f"<管理员> 【账户刷新】 账户：{user} 刷新失败！请检查AC_Token是否有效！")

    @st.experimental_dialog("生成刷新令牌")
    def new_refresh():
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            rf_group = st.selectbox("**组别**", accounts.keys(), key="rf_group_new")
            site_limit = st.text_input("**限制网站（为空不限制）**", value="", help="限制的网站, 为空则不限制", key="site_limit_new")
            expires_in = st.number_input("**有效期（秒**）", value=0, help="token有效期（单位为秒），填 0 则永久有效", key="expires_in_new")
        with col2:
            gpt35_limit = st.number_input("**限制GPT-3.5**", value=-1, help="GPT-3.5对话限制，填 -1 则不限制", key="gpt35_limit_new")
            gpt4_limit = st.number_input("**限制GPT-4**", value=-1, help="GPT-4对话限制，填 -1 则不限制", key="gpt4_limit_new")
            show_conversations = st.selectbox("**会话无需隔离**", ['true', 'false'], index=1, help="false为隔离会话", key="show_conversations_new")
        note = st.text_input("**备注**", value="2024", help="备注信息，可为空", key="note_new")
        auto_rf_gen = st.checkbox("**批量生成**")
        if auto_rf_gen:
            num_rf_gen = st.number_input("**生成数量**", value=5, min_value=1, max_value=100, key="num_rf_gen_new")
            len_rf_gen = st.number_input("**刷新令牌长度**", value=16, min_value=16, max_value=32, key="len_rf_gen_new")
        else:
            rf_token = st.text_input("**刷新令牌**", value="rf-", key="rf_token_new")

        st.write("")
        if st.button("**生成刷新令牌**", use_container_width=True, key="new_refresh"):
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
            sac.alert(label="生成成功！", color="success", variant='filled', size="md", radius="lg", icon=True, closable=True)
            time.sleep(0.5)
            sac.alert(label="即将自动刷新！", color="success", variant='filled', size="md", radius="lg", icon=True, closable=True)
            time.sleep(1.5)
            st.rerun()
        st.write("")


    st.write("## 欢迎！" + web_setting["web"]["super_user"])

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
            st.write("")
            st.write("**站点信息**")

            user_names = config.keys()
            size_bytes1 = os.path.getsize(current_path + "app.log")
            size_bytes2 = 0
            for file in os.listdir("config"):
                size_bytes2 += os.path.getsize("config/" + file)

            if size_bytes1 == 0:
                size1 = "0B"
            else:
                size_name = ("B", "KB", "MB", "GB", "TB")
                i = int(math.floor(math.log(size_bytes1, 1024)))
                p = math.pow(1024, i)
                s = round(size_bytes1 / p, 2)
                size1 = f"{s} {size_name[i]}"

            if size_bytes2 == 0:
                size2 = "0B"
            else:
                size_name = ("B", "KB", "MB", "GB", "TB")
                i = int(math.floor(math.log(size_bytes2, 1024)))
                p = math.pow(1024, i)
                s = round(size_bytes2 / p, 2)
                size2= f"{s} {size_name[i]}"

            if "count_people" not in st.session_state:
                st.session_state.count_people = 0
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("用户总数", len(user_names), len(user_names)-3)
            col2.metric("号池总数", len(accounts.keys()), len(accounts.keys())-1)
            col3.metric("服务累计", st.session_state.count_people, st.session_state.count_people)
            col4.metric("日志信息", size1, size_bytes1-36)
            col5.metric("配置信息", size2, size_bytes2-3755)

            with col1:
                if st.button("**导出配置**", use_container_width=True):
                    download()
            with col2:
                if st.button("**导入配置**", use_container_width=True):
                    upload()

            st.divider()
            with open(current_path + 'app.log', 'r', encoding='utf-8') as file:
                lines = file.readlines()
            with open(current_path + 'app.log', 'r', encoding='utf-8') as file:
                logs = file.read()
            pattern = re.compile(r'(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2},\d{3} - INFO - 【用户登录】 用户：(\w+) 登录成功！')
            pattern_share = re.compile(r'(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2},\d{3} - INFO - 【Share登录】 共享账户：(\w+) 被登录！')
            pattern_sign = re.compile(r'(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2},\d{3} - INFO - 【用户注册】 新用户：(\w+) 注册成功！')

            matches_user = pattern.findall(logs)
            matches_share = pattern_share.findall(logs)
            matches_sign = pattern_sign.findall(logs)

            st.write('**服务总览**')
            plot_choose = sac.segmented(
                items=[
                    sac.SegmentedItem(label='登录统计柱状图', icon='bar-chart-line'),
                    sac.SegmentedItem(label='登录统计折线图', icon='graph-up'),
                    sac.SegmentedItem(label='用户服务统计图', icon='person-video3'),
                    sac.SegmentedItem(label='共享服务统计图', icon='share'),
                    sac.SegmentedItem(label='注册人数统计图', icon='door-open'),
                ], color='dark', use_container_width=True
            )

            if plot_choose == '登录统计柱状图':
                if matches_user or matches_share:
                    matches = matches_user + matches_share
                    st.session_state.count_people = len(matches)
                    data = pd.DataFrame(matches, columns=['日期', 'user'])
                    summary = data.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.write("")
                    st.bar_chart(pivot_table)
                else:
                    sac.alert(label="暂无服务记录，快去使用吧！", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    col1, col2, col3 = st.columns([0.46, 0.08, 0.46])
                    with col2:
                        st.image("LOGO.png", caption="图表", width=200, use_column_width=True)

            if plot_choose == '登录统计折线图':
                if matches_user or matches_share:
                    matches = matches_user + matches_share
                    df = pd.DataFrame(matches, columns=['date', 'user'])
                    user_login_counts = df.groupby(['date', 'user']).size().unstack(fill_value=0).reset_index()
                    user_login_counts['total_logins'] = user_login_counts.select_dtypes(include=['number']).sum(axis=1)
                    st.line_chart(data=user_login_counts.set_index('date'), use_container_width=True)
                else:
                    sac.alert(label="暂无服务记录，快去使用吧！", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    col1, col2, col3 = st.columns([0.46, 0.08, 0.46])
                    with col2:
                        st.image("LOGO.png", caption="图表", width=200, use_column_width=True)

            if plot_choose == '用户服务统计图':
                if matches_user:
                    data = pd.DataFrame(matches_user, columns=['日期', 'user'])
                    summary = data.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.write("")
                    st.bar_chart(pivot_table)
                else:
                    sac.alert(label="暂无服务记录，快去使用吧！", color="warning", variant='quote', size="md",radius="lg", icon=True, closable=True)
                    col1, col2, col3 = st.columns([0.46, 0.08, 0.46])
                    with col2:
                        st.image("LOGO.png", caption="图表", width=200, use_column_width=True)

            if plot_choose == '共享服务统计图':
                if matches_share:
                    data = pd.DataFrame(matches_share, columns=['日期', 'user'])
                    summary = data.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.write("")
                    st.bar_chart(pivot_table)
                else:
                    sac.alert(label="暂无服务记录，快去使用吧！", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    col1, col2, col3 = st.columns([0.46, 0.08, 0.46])
                    with col2:
                        st.image("LOGO.png",caption="图表", width=200, use_column_width=True)

            if plot_choose == '注册人数统计图':
                print(matches_sign)
                if matches_sign:
                    data = pd.DataFrame(matches_sign, columns=['日期', 'user'])
                    summary = data.groupby(['日期', 'user']).size().reset_index(name='注册总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='注册总计').fillna(0)
                    st.write("")
                    st.bar_chart(pivot_table)
                else:
                    sac.alert(label="暂无服务记录，快去使用吧！", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    col1, col2, col3 = st.columns([0.46, 0.08, 0.46])
                    with col2:
                        st.image("LOGO.png", caption="图表", width=200, use_column_width=True)

            st.divider()
            st.write("**运行日志**")
            st.write("")
            lines.reverse()
            result_str = "".join(str(line) for line in lines)
            st.text_area("运行日志", value=result_str, height=300, label_visibility="collapsed")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.write("")
                if st.button("**清理日志**", use_container_width=True):
                    log_content = "【OaiT服务已成功开启！】\n"
                    with open(current_path + "app.log", "w", encoding="utf-8") as log_file:
                        log_file.write(log_content)
                    st.rerun()
                st.write("")

    if set_choose == '基本设置':
        if not web_setting["web"]["readme"]:
            readme()
        with st.container(border=True):
            st.write("")
            st.write("**网站设置**")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("**站点标题**", value=web_setting["web"]["title"])
                subtitle = st.text_input("**站点副标题**", value=web_setting["web"]["subtitle"])
            with col2:
                super_user = st.text_input("**管理员昵称**", value=web_setting["web"]["super_user"])
                super_key = st.text_input("**管理员密钥**", value=web_setting["web"]["super_key"], type="password")

            st.write("")
            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                if st.button(" **保存设置**", use_container_width=True):
                    web_setting["web"]["title"] = title
                    web_setting["web"]["subtitle"] = subtitle
                    web_setting["web"]["super_user"] = super_user
                    web_setting["web"]["super_key"] = super_key
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    logger.info(f"<管理员> 【基本设置】 更新了网站基本设置！")
                    st.toast("保存成功!", icon=':material/check_circle:')

            st.divider()
            st.write("**服务域名**")
            sac.alert(label="**类型中 `Newest` 表示最新UI， `Classic` 表示Pandora 经典UI**", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            rows = [[datas['name'], name, datas['speed'], datas['type']]
                    for name, datas in domain_data.items()]
            df0 = pd.DataFrame(rows, columns=["命名", "服务域名", "延迟", "类型"])

            col1, col2 = st.columns(2)
            try:
                with col1:
                    choose_domain = st.selectbox("**是否允许用户选择线路**", ["允许", "不允许"], index=["允许", "不允许"].index(web_setting["web"]["choose_domain"]))
            except:
                with col1:
                    choose_domain = st.selectbox("**是否允许用户选择线路**", ["允许", "不允许"], index=1)
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
            st.write("")
            data = st.data_editor(df0, hide_index=True, use_container_width=True, height=143, num_rows="dynamic", disabled=["延迟"], column_config={"类型": st.column_config.SelectboxColumn(options=["Newest", "Classic"])})
            st.write("")

            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                if st.button("**保存修改**", use_container_width=True, key="save_domain"):
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
                    st.toast("保存成功!", icon=':material/check_circle:')
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
            with col7:
                if st.button("**测试延迟**", use_container_width=True):
                    delay = []
                    for i in rows:
                        try:
                            start_time = time.time()
                            response = requests.get("https://" + i[1])
                            end_time = time.time()
                            total_time = end_time - start_time
                            delay.append(str(round(total_time, 5)) + "s")
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
                col3, col4 = st.columns(2)
                with col3:
                    notice_enable = st.checkbox("**开启站点公告**", value=web_setting["web"]["notice_enable"])
                with col4:
                    notice_banner = st.checkbox("**公告滚动效果**", value=web_setting["web"]["notice_banner"])
                notice_title = st.text_area("**站点公告-主标题(支持markdown)**", value=web_setting["web"]["notice_title"], height=100)
                notice_subtitle = st.text_area("**站点公告-次标题(支持markdown)**", value=web_setting["web"]["notice_subtitle"], height=100)
            with col2:
                style = ['light', 'filled', 'outline', 'transparent', 'quote', 'quote-light']
                color = ['success', 'info', 'warning', 'error', 'dark', 'gray', 'red', 'pink', 'grape', 'violet', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange']
                size = ['xs', 'sm', 'md', 'lg', 'xl']
                col3, col4 = st.columns(2)
                with col3:
                    notice_size = st.selectbox("**公告大小**", size, index=size.index(web_setting["web"]["notice_size"]))
                    notice_radius = st.selectbox("**公告圆角**", size, index=size.index(web_setting["web"]["notice_radius"]))
                with col4:
                    notice_style = st.selectbox("**公告样式**", style, index=style.index(web_setting["web"]["notice_style"]))
                    notice_color = st.selectbox("**公告颜色**", color, index=color.index(web_setting["web"]["notice_color"]))
                st.write("")
                st.write("**样式预览**")

                sac.alert(label=notice_title, description=notice_subtitle,
                          color=notice_color, banner=notice_banner,
                          variant=notice_style, size=notice_size, radius=notice_radius, icon=True, closable=True)

            st.write("")
            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                if st.button("**保存修改**", use_container_width=True, key="save_notice"):
                    web_setting["web"]["notice_enable"] = notice_enable
                    web_setting["web"]["notice_enable"] = notice_enable
                    web_setting["web"]["notice_banner"] = notice_banner
                    web_setting["web"]["notice_size"] = notice_size
                    web_setting["web"]["notice_radius"] = notice_radius
                    web_setting["web"]["notice_style"] = notice_style
                    web_setting["web"]["notice_title"] = notice_title
                    web_setting["web"]["notice_color"] = notice_color
                    web_setting["web"]["notice_subtitle"] = notice_subtitle
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    logger.info(f"<管理员> 【公告设置】 更新了站点公告！")
                    st.toast("保存成功!", icon=':material/check_circle:')
            st.write("")

    if set_choose == '号池管理':
        with st.container(border=True):
            st.write('')
            rows = [[groups, datas['account_type'], datas['account'], datas['access_token'], datas['refresh_token']]
                    for groups, datas in accounts.items()]
            st.write("**号池列表**")
            sac.alert(label="**`用户组` 是每个账号的唯一标识，`不允许名称相同！`**", description="用户组是各个模块相互联系的重要关键字，命名后请谨慎修改！", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            df1 = pd.DataFrame(rows, columns=['用户组', '订阅类型', '账户邮箱', 'AC_Token', 'RF_Token'])
            edited_df1 = st.data_editor(df1, hide_index=True, use_container_width=True, num_rows="dynamic", height=248, column_config={"订阅类型": st.column_config.SelectboxColumn(options=["Free", "Plus"])})

            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                if st.button("**保存修改**", use_container_width=True):
                    json_data1 = df_to_json1(edited_df1)
                    json_filename = 'accounts.json'
                    with open(current_path + json_filename, 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data1)
                    logger.info(f"<管理员> 【账户更改】 更新了账户信息！")
                    st.toast("保存成功!", icon=':material/check_circle:')
            with col7:
                if st.button("**新增账户**", use_container_width=True):
                    new_account()
            with col8:
                st.link_button("**获取RF_Token**", "https://token.oaifree.com/auth", use_container_width=True)

            st.divider()
            st.write("**邀请令牌**")
            sac.alert(label="**您必须重新设置 `至少一个注册码`，同一个组别 `允许对应多个邀请码`。**", variant='quote', color="warning", size="md", radius="lg", icon=True, closable=True)

            invite_link_enable = st.checkbox("**显示发卡链接**", value=web_setting["web"]["invite_link_enable"], key="invite_link_enable")
            invite_link = st.text_input("**发卡链接(完整网址)**", value=web_setting["web"]["invite_link"], key="invite_link")
            st.write("")
            rows = [[IV_Token, invite_config[IV_Token]["group"], invite_config[IV_Token]["note"], invite_config[IV_Token]["used"]] for IV_Token, Group in invite_config.items()]
            df3 = pd.DataFrame(rows, columns=['Invite_Token', '用户组', '备注', '是否使用'])

            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=0, key="hide_index_invite")
                    if st.button("删除已用令牌", use_container_width=True, key="delete_invite"):
                        for i in list(invite_config.keys()):
                            if invite_config[i]["used"]:
                                invite_config.pop(i)
                        with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                            json.dump(invite_config, f, indent=2)
                        st.toast("删除成功!", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【邀请令牌】 删除了已使用的邀请令牌！")
                        st.rerun()
                with col2:
                    height = st.number_input("**表格高度**", value=248, min_value=100, max_value=1000, step=100, key="height_invite")
                    if st.button("删除所有令牌", use_container_width=True, key="delete_all_invite"):
                        invite_config.clear()
                        with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                            json.dump(invite_config, f, indent=2)
                        st.toast("删除成功!", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【邀请令牌】 删除了所有的邀请令牌！")
                        st.rerun()
                with col3:
                    order_what = st.selectbox("**排序列名**", ["Invite_Token", "用户组", "备注", "是否使用"], index=3, key="order_what")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=0, key="order_row")
                with col5:
                    order = st.multiselect("**数据显示**", ["Invite_Token", "用户组", "备注", "是否使用"], key="order")

                if order_row == "升序":
                    df3 = df3.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df3 = df3.sort_values(by=order_what, ascending=False)

            edited_df3 = st.data_editor(df3, hide_index=hide_index, use_container_width=True, height=height, column_order=order, num_rows="dynamic", column_config={"group": st.column_config.SelectboxColumn(options=accounts.keys())}, disabled=["是否使用"])

            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存修改**", use_container_width=True, key="save_invite"):
                    web_setting["web"]["invite_link_enable"] = invite_link_enable
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
                        st.toast("保存成功!", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【邀请码更改】 更新了邀请码信息！")
                    else:
                        with col6:
                            sac.alert(label="保存失败！您必须设置完整的注册码并选择正确的组别，不允许为空值!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
            with col2:
                if st.button("**配置新用户权限**", use_container_width=True):
                    invite()
            with col3:
                if st.button("**生成邀请令牌**", use_container_width=True, key="new_invite_token"):
                    new_invite()

            st.divider()
            st.write("**AC_Token刷新**")
            sac.alert(
                label="**开启后登陆时会自动检测用户的 `SA_Token`，如果状态获取失败则会自动尝试刷新 `SA_Token` 和 `AC_Token` ，实现 `自动化刷新管理用户状态`**",
                description="**已对限制时间的用户（expires_in不为0）进行单独优化，开启后 `不会重置受限用户的时间数`。**",
                color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            refresh = st.checkbox("**登陆时自动检测并刷新AC状态**", value=web_setting["web"]["refresh_all"])

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存修改**", use_container_width=True, key="save_AC_Token刷新"):
                    web_setting["web"]["refresh_all"] = refresh
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)

            st.divider()
            st.write("**手动AC_Token刷新**")
            group = st.selectbox("**选择需要刷新用户组**", accounts.keys())
            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                st.write("")
                if st.button(f"**刷新 - {group}**", use_container_width=True):
                    status, new_access_token = get_accesstoken(accounts[group]['refresh_token'])
                    if status:
                        st.toast(f"刷新成功！", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【刷新AC_Token】 刷新了 {group} 组的 AC_Token！")
                        accounts[group]['access_token'] = new_access_token
                        with open(current_path + "accounts.json", "w", encoding="utf-8") as f:
                            json.dump(accounts, f, indent=2)
                    else:
                        with col6:
                            logger.error(f"<管理员> 【刷新AC_Token】 刷新 {group} 组的 AC_Token 失败！")
                            sac.alert(label="刷新失败！", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
            st.write("")

    if set_choose == '用户管理':
        with st.container(border=True):
            st.write('')
            st.write("**用户列表**")
            sac.alert(label="**所有表格均支持 `搜索`、`下载`、`新建`、`删除`、`修改`、`排序` ，但请务必在修改后进行保存！**", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)

            fields = ['账户', '密码', 'SA_Token', '用户组', '订阅类型', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离']
            rows = [[user] + list(account.values()) for user, account in config.items()]
            df2 = pd.DataFrame(rows, columns=fields)
            edited_df2 = st.data_editor(df2, hide_index=True, use_container_width=True, height=248, disabled=['用户组', '订阅类型', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离'], num_rows="dynamic")

            st.write('')
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存修改** ", use_container_width=True, key="save_user"):
                    json_data2 = df_to_json2(edited_df2)
                    with open(current_path + 'config.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data2)
                    st.toast("保存修改成功！", icon=':material/check_circle:')
                    logger.info(f"<管理员> 【用户更改】 更新了用户信息！")
            with col2:
                if st.button("**状态刷新**", use_container_width=True):
                    refresh_user()
            with col3:
                st.link_button("**获取SA_Token**", "https://chat.oaifree.com/token", use_container_width=True)


            st.divider()
            st.write("**刷新令牌**")
            sac.alert(
                label="**开启后受限用户可以在主页的 `无法登录？` 内自行刷新 `AC_Token`，以实现自助刷新，您可以通过设置不同的令牌来管理 用户刷新后的可用时间**",
                color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            col1, col2 = st.columns(2)
            with col1:
                user_refresh = st.checkbox("**过期用户可自行刷新SA_Token状态**", value=web_setting["web"]["user_refresh"])
            with col2:
                refresh_link_enable = st.checkbox("**显示发卡链接**", value=web_setting["web"]["refresh_link_enable"], key="refresh_link_enable")
            refresh_link = st.text_input("**发卡链接(完整网址)**", value=web_setting["web"]["refresh_link"], key="refresh_link")

            fields = ['userRF_Token', '用户组', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离', '备注', '是否使用']
            rows = [[rf_token] + list(datas.values()) for rf_token, datas in refresh_data.items()]
            df4 = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=0, key="hide_index_refresh")
                    if st.button("删除已用令牌", use_container_width=True, key="delete_refresh"):
                        for i in list(refresh_data.keys()):
                            if refresh_data[i]["used"]:
                                refresh_data.pop(i)
                        with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                            json.dump(refresh_data, f, indent=2)
                        st.toast("删除成功!", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【刷新令牌】 删除了已使用的刷新令牌！")
                        st.rerun()
                with col2:
                    height = st.number_input("**表格高度**", value=248, min_value=100, max_value=1000, step=100, key="height_refresh")
                    if st.button("删除所有令牌", use_container_width=True, key="delete_all_refresh"):
                        refresh_data.clear()
                        with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                            json.dump(refresh_data, f, indent=2)
                        st.toast("删除成功!", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【刷新令牌】 删除了所有的刷新令牌！")
                        st.rerun()
                with col3:
                    order_what = st.selectbox("**排序列名**", ['userRF_Token', '用户组', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离', '备注', '是否使用'], index=8, key="order_what")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=0, key="order_row_refresh")
                with col5:
                    order = st.multiselect("**数据显示**", ['userRF_Token', '用户组', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离', '备注', '是否使用'], ['userRF_Token', '用户组', '过期秒数', 'GPT3.5限制', 'GPT4限制', '备注', '是否使用'], key="order_refresh")

                if order_row == "升序":
                    df4 = df4.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df4 = df4.sort_values(by=order_what, ascending=False)

            edited_df4 = st.data_editor(df4, hide_index=hide_index, use_container_width=True, height=height, num_rows="dynamic", disabled=["是否使用"], column_order=order, column_config={"用户组": st.column_config.SelectboxColumn(options=accounts.keys())})
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存修改**", use_container_width=True, key="save_refresh"):
                    web_setting["web"]["user_refresh"] = user_refresh
                    web_setting["web"]["refresh_link_enable"] = refresh_link_enable
                    web_setting["web"]["refresh_link"] = refresh_link
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    json_data4 = df_to_json4(edited_df4)
                    with open(current_path + 'refresh.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data4)
                    st.toast("保存成功！", icon=':material/check_circle:')
                    logger.info(f"<管理员> 【刷新令牌】 更新了刷新令牌信息！")
            with col2:
                if st.button("**生成刷新令牌**", use_container_width=True, key="new_refresh_token"):
                    new_refresh()
            st.write("")

            st.divider()
            st.write("**用户注册 - 管理员**")
            sac.alert(label="**说明：`限制网站`为 空 则无限制；`过期秒数` 为 0 则永不过期；`GPT3.5限制` 为 -1 则无限制；`GPT4限制` 为 -1 则无限制；`会话无需隔离` 为 true 则不隔离会话**",color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            col1, col2 = st.columns(2)
            with col1:
                user_new_acc = st.text_input("**账户**")
                user_new_pass = st.text_input("**密码**")
                user_new_group = st.selectbox("**组别**", accounts.keys())
                show_conversations = st.selectbox("**会话无需隔离**", ['true', 'false'], index=1, help="false为隔离会话")
            with col2:
                site_limit = st.text_input("**限制网站（为空不限制）**", value="", help="限制的网站, 为空则不限制")
                expires_in = st.number_input("**有效期（秒**）", value=0, help="token有效期（单位为秒），填 0 则永久有效")
                gpt35_limit = st.number_input("**限制GPT-3.5**", value=-1, help="GPT-3.5对话限制，填 -1 则不限制")
                gpt4_limit = st.number_input("**限制GPT-4**", value=-1, help="GPT-4对话限制，填 -1 则不限制")
            st.write('')
            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**注册该用户**", use_container_width=True):
                    if user_new_acc == "":
                        with col6:
                            sac.alert(label="请填写账户!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    elif user_new_pass == "":
                        with col6:
                            sac.alert(label="请填写密码!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    elif user_new_acc in config:
                        with col6:
                            sac.alert(label="该账户已存在!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    else:
                        group_data = accounts[user_new_group]
                        acc = group_data['access_token']
                        status, new_name, new_token_key = get_sharetoken(user_new_acc, acc, site_limit, expires_in, gpt35_limit, gpt4_limit, show_conversations)

                        json_data = {
                            new_name: {
                                'password': user_new_pass,
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
                        st.toast("注册成功！", icon=':material/check_circle:')
                        st.toast("即将刷新页面...1s", icon=':material/check_circle:')
                        time.sleep(1)
                        logger.info(f"<管理员> 【用户注册】 新用户注册成功！name：{new_name}，token:{new_token_key}，group:{user_new_group}")
                        st.rerun()

                st.write("")
            with col2:
                if st.button("**前往首页登录**", use_container_width=True):
                    st.switch_page("home.py")

    if set_choose == '更多功能':
        with st.container(border=True):
            st.write('')
            st.write("**Share共享站**")
            share = st.checkbox("**开启Share功能**", value=web_setting["web"]["share"])
            if share:
                share_notice = st.text_area("**Share站公告**(支持MarkDown)", value=web_setting["web"]["share_notice"])
                share_list = share_data.keys()
                index = []
                for i in share_list:
                    index.append(list(config.keys()).index(i))
                share_account = sac.transfer(items=config.keys(), index=index, titles=['现有用户池', '共享账号池'], use_container_width=True, reload=True, align='center', search=True, pagination=True, width=500, height=400, color="dark")

            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存更改**", use_container_width=True):
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
                if st.button("**前往Share站**", use_container_width=True):
                    st.switch_page("pages/share.py")

            st.divider()
            st.write("**关于**")
            st.write("版本：OaiT V1.1.2")
            st.write("作者：@Chenyme")
            st.write("鸣谢：@Neo")
            st.write("GitHub：https://github.com/Chenyme/oaifree-tools")
            st.write("有任何问题欢迎提 issue，如果觉得好用请给我一个 Star 吧，感谢支持！")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**更多**", use_container_width=True):
                    readme()

            st.divider()
            st.write("**友情链接**")
            st.write("下面是 Neo博客、Linux论坛、项目框架、个人其他项目的链接，欢迎访问！")
            sac.buttons([sac.ButtonsItem("GitHub", href="https://github.com/Chenyme", color="dark"), sac.ButtonsItem("Linux.do", href="https://linux.do", color="dark"), sac.ButtonsItem("zhile.io", href="https://zhile.io/", color="dark"), sac.ButtonsItem("Streamlit", href="https://streamlit.io", color="dark"), sac.ButtonsItem("我的其他项目", href="https://github.com/Chenyme/Chenyme-AAVT", color="dark")], use_container_width=True, color="dark", index=None, variant="filled")

    col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
    with col2:
        st.image("LOGO.png", width=200, caption="一键管理Oaifree镜像服务，简单上手", use_column_width=True)


else:
    col1, col2, col3 = st.columns(3)
    with col2:
        sac.alert("**非法访问！**", "**警告：你无权进入该页面！**", color="error", size="lg", radius="lg", icon=True, variant="filled", closable=True)
        with st.container(border=True):
            col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
            with col2:
                st.image("LOGO.png", width=200, use_column_width=True)
            st.write("")
            admin = st.text_input("**管理账户：**")
            st.write("")
            key = st.text_input("**管理密钥：**", type="password")
            st.write("")
            st.write("")
            if st.button("**验证身份**", use_container_width=True):
                if admin == web_setting["web"]["super_user"] and key == web_setting["web"]["super_key"]:
                    st.session_state.role = "admin"
                    logger.info(f"【管理登录】 管理员：{admin} 登录成功！")
                    st.write("")
                    st.switch_page("pages/admin.py")
                else:
                    sac.alert(label="身份验证失败！", color="error", variant='quote', size="lg", radius="lg", icon=True,
                              closable=True)
            st.write("")
            st.write("")
            st.write("")
