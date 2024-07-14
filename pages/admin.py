# -*- coding: utf-8 -*-
# v1.2.0 @Chenyme
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
from utils import get_accesstoken, get_sharetoken, df_to_json1, df_to_json_oaifree, df_to_json_invite, df_to_json4, \
    df_to_json_fuclaude, df_to_json_user_data, check_sharetoken, get_size

# 运行日志
style_path = os.path.abspath('.') + '/style/'
current_path = os.path.abspath('.') + '/config/'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(current_path + "/app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

# 读取配置文件
with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
    web_setting = toml.load(file)
with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
    accounts = json.load(file)
with open(current_path + '/users.json', 'r', encoding='utf-8') as file:
    user_data = json.load(file)
with open(current_path + '/domain.json', 'r', encoding='utf-8') as file:
    domain_data = json.load(file)
with open(current_path + '/openai.json', 'r', encoding='utf-8') as file:
    openai_data = json.load(file)
with open(current_path + '/invite.json', 'r', encoding='utf-8') as file:
    invite_config = json.load(file)
with open(current_path + '/anthropic.json', 'r', encoding='utf-8') as file:
    anthropic_data = json.load(file)
with open(current_path + '/share.json', 'r', encoding='utf-8') as file:
    share_data = json.load(file)
with open(current_path + '/refresh.json', 'r', encoding='utf-8') as file:
    refresh_data = json.load(file)
with open(style_path + "//sidebar.html", "r", encoding="utf-8") as file:
    sidebar_html = file.read()
with open("LOGO.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

openai_list = []
anthropic_list = []
for key, value in accounts.items():
    if value["service_provider"] == "OpenAI":
        openai_list.append(key)
    else:
        anthropic_list.append(key)

version = "v1.2.0"
st.set_page_config(layout="wide",
                   page_title=web_setting["web"]["title"],
                   page_icon="LOGO.png",
                   initial_sidebar_state="expanded")

# 管理页面主题
with open(style_path + '/admin.html', 'r', encoding='utf-8') as file:
    st.markdown(file.read(), unsafe_allow_html=True)
    button_type = "secondary"

# 阻止非法访问
if "role" not in st.session_state:
    st.session_state.role = None

if "theme" not in st.session_state:
    st.session_state.theme = web_setting["web"]["login_theme"]

if "success" in st.session_state:
    st.toast("**更改成功！**", icon=":material/check_circle:")
    del st.session_state.success

if "test" in st.session_state:
    st.toast("**测试成功！**", icon=":material/check_circle:")
    del st.session_state.test

if "add" in st.session_state:
    st.toast("**新增成功！**", icon=":material/check_circle:")
    del st.session_state.add

if "delete" in st.session_state:
    st.toast("**删除成功！**", icon=":material/check_circle:")
    del st.session_state.delete

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
        st.warning("**首次登入请及时修改管理密钥！**", icon=':material/sd_card_alert:')
        st.write("")
        new_super_user = st.text_input("**新的昵称**", placeholder="请输入您的新昵称！")
        new_super_key = st.text_input("**新的密钥**", type="password", placeholder="请输入您的新密钥！")
        st.write("")
        if st.button("**保存更改**", use_container_width=True, type=button_type):
            if new_super_user == "" or new_super_user is None:
                st.error("**昵称不可为空，请重新输入！**", icon=":material/error:")
            elif len(new_super_key) < 8:
                st.error("**密钥长度不得小于 8 位，请重新输入！**", icon=":material/error:")
            elif new_super_key == "12345678":
                st.error("**请勿使用默认密钥，重新输入！**", icon=":material/error:")
            else:
                web_setting["web"]["super_user"] = new_super_user
                web_setting["web"]["super_key"] = new_super_key
                logger.info(f"【安全保护】 管理员修改了新的密钥！")
                with open(current_path + "/setting.toml", "w", encoding="utf-8") as file:
                    toml.dump(web_setting, file)
                st.session_state.success = True
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
        st.info("""
        本项目为开源项目，使用者必须在遵循 OpenAI 和 Claude 的 **使用条款** 以及 **法律法规** 的情况下使用，不得用于非法用途。

        根据[**《生成式人工智能服务管理暂行办法》**](http://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)的要求，请勿对中国地区公众提供一切未经备案的生成式人工智能服务。""")

        st.markdown("""
            - **制作不易，不许白嫖，请给一颗免费的心叭！开源项目可自由魔改，但请保留原作者信息并遵循开源协议。**
            - **OaiT 后台功能一览：**
            
                - **服务总览**：服务统计/图表数据/站点迁移/运行日志
                - **域名管理**：域名列表/服务切换/延迟测速/自定义域名
                - **主题样式**：管理信息/网站设置/主题切换/公告设置
                - **号池管理**：账号总览/账号刷新/邀请令牌/刷新令牌
                - **用户管理**：用户总览/用户注册/Oaifree/Fucluade
                - **更多功能**：共享服务/Oai-APi（暂未开发）/关于项目
                
            ---
            - **注意事项：**
                - 新版本配置文件可能不同，导入时请注意版本兼容性
                - 修改后请及时检查并保存，否则可能会导致数据丢失
                - 新增号池注意用户组命名，不可重复，否则会自动覆盖
                - **若使用中框内出现 "Press Enter To Apply" 字样，请及时按回车或点击页面空白处以确认，否则可能登录失败！**
                
            ---
            - **特别鸣谢：**
                - **感谢始皇！没有始皇的努力这一切都是徒劳！**
                
            # OpenAI，Not CloseAI！愿开源精神永存！
            ---
        """)

        if st.button("**我已知晓，不再弹出**", use_container_width=True, type=button_type):
            web_setting["web"]["readme"] = True
            with open(current_path + "/setting.toml", "w", encoding="utf-8") as file:
                toml.dump(web_setting, file)
            st.rerun()
        st.link_button("**来GitHub给我一颗星叭！**", "https://github.com/Chenyme/oaifree-tools",
                       use_container_width=True, type=button_type)


    @st.experimental_dialog("站点迁移 - 数据导出")
    def download():
        with st.expander("**数据文件说明**", expanded=False):
            st.info("""
            **app.log： 运行日志**

            **users.json： 用户信息**

            **share.json： 共享信息**

            **domain.json： 域名信息**

            **setting.toml： 基本设置**

            **accounts.json： 号池信息**

            **invite.json： 邀请令牌信息**

            **refresh.json： 刷新令牌信息**

            **openai.json： OpenAI 用户信息**

            **anthropic.json： Anthropic 用户信息**
            """)

        st.info("**正在准备数据，请稍后...**", icon=":material/double_arrow:")
        files = ["app.log", "users.json", "share.json", "domain.json", "setting.toml", "accounts.json", "invite.json", "refresh.json", "openai.json", "anthropic.json"]
        directory_path = current_path
        zip_buffer = BytesIO()

        try:
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
                        st.success(f"**{file}**", icon=":material/check_circle:")
                if i % 2 == 0:
                    with col2:
                        st.success(f"**{file}**", icon=":material/check_circle:")
                i += 1
            st.write("")
            st.download_button(label="**下载数据**", data=zip_buffer, file_name="config.zip", mime="application/zip", use_container_width=True, type=button_type)
        except:
            st.write("")
            st.error("**数据导出失败，请重试！**", icon=":material/error:")
        st.write("")

    @st.experimental_dialog("站点迁移-数据导入")
    def upload():
        st.write("")
        st.write("**请上传配置文件**")
        st.warning("""

        **仅支持 V1.2.0 版本后的配置文件导入！**

        **请慎重上传 V1.1.x 或 更早版本 的配置文件！**

        """, icon=':material/sd_card_alert:')
        uploaded_file = st.file_uploader("上传文件", type=['zip'], label_visibility="collapsed")
        required_files = ["app.log", "users.json", "share.json", "domain.json", "setting.toml", "accounts.json", "invite.json", "refresh.json", "openai.json", "anthropic.json"]
        if st.button("**数据迁移**", use_container_width=True, type=button_type):
            if uploaded_file is not None:
                zip_buffer = BytesIO(uploaded_file.getvalue())
                with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                    zip_file_list = zip_ref.namelist()
                    success_files = [file for file in required_files if file in zip_file_list]
                    error_files = [file for file in zip_file_list if file not in required_files]
                    st.info("**正在迁移数据，请稍后...**", icon=":material/double_arrow:")
                    col1, col2 = st.columns(2)
                    i = 1
                    for file in success_files:
                        zip_ref.extract(file, current_path)
                        if i % 2 == 1:
                            with col1:
                                st.success(f"**{file}**", icon=":material/check_circle:")
                        if i % 2 == 0:
                            with col2:
                                st.success(f"**{file}**", icon=":material/check_circle:")
                        i += 1
                    for file in error_files:
                        st.error(f"**未知文件{file}**", icon=":material/error:")
                st.success("**数据迁移成功！**", icon=":material/check_circle:")
            else:
                st.error("**请先上传数据文件！**", icon=":material/error:")
        st.write("")


    @st.experimental_dialog("新增服务域名")
    def add_domain():
        st.write("")
        new_domain_name = st.text_input("**服务名称**", placeholder="请输入此服务的显示名称！")
        new_domain_url = st.text_input("**服务链接**",  placeholder="请输入此服务的指向链接！例：new.oaifree.com")
        new_domain_type = st.selectbox("**服务类型**", ["Oaifree", "Pandora", "Fuclaude"], index=0, help="Fuclaude 指向 claude UI， Oiafree 指向 ChatGPT UI， Pandora 指向 Pandora 经典UI")
        new_domain_delay = st.number_input("**服务延迟**", value=0, disabled=True, help="自动测速，无需填写！")
        st.write("")
        if st.button("**新增此服务**", use_container_width=True, type=button_type):
            if new_domain_name == "":
                st.write("")
                sac.alert(label="**服务名称不可为空，请重新填写！**", color="error", variant='filled', size="md", radius="md", icon=True)
            elif new_domain_url == "":
                st.write("")
                sac.alert(label="**服务链接不可为空，请重新填写！**", color="error", variant='filled', size="md", radius="md", icon=True)
            elif new_domain_url in domain_data.keys():
                st.write("")
                sac.alert(label="**此服务链接已存在，请重新填写！**", color="error", variant='filled', size="md", radius="md", icon=True)
            else:
                domain_data[new_domain_url] = {
                    "name": new_domain_name,
                    "speed": new_domain_delay,
                    "type": new_domain_type
                }
                with open(current_path + "domain.json", "w", encoding="utf-8") as file:
                    json.dump(domain_data, file, indent=2)
                logger.info(f"【管理员】 新增了服务域名 {new_domain_name}！")
                st.session_state.add = True
                st.rerun()
        st.write("")


    @st.experimental_dialog("新增账户")
    def new_account():
        st.write("")
        new_group = st.text_input("**命名新用户组***", value="", help="所有模块串联的唯一标识，不可为空", placeholder="唯一标识，不可为空！")
        col1, col2 = st.columns(2)
        with col1:
            new_service_provider = st.selectbox("**服务商**", ["Anthropic", "OpenAI"], index=0, help="服务商选择，不可为空！")
        with col2:
            new_account_type = st.selectbox("**订阅类型***", ["Free", "Plus"], index=1, help="订阅套餐情况，不可为空！")

        if new_service_provider == "Claude":
            new_account = st.text_input("**账户邮箱**", value="", help="账户邮箱，用于标识备注，可为空", placeholder="账户邮箱，仅用于自我备注，可为空！")
            new_access_token = st.text_input("**SE_Token***", help="SS_Token，刷新时的重要Token，不可为空", placeholder="SS_Toke，刷新时的重要Token，不可为空！")
            new_refresh_token = "Claude服务暂无此项"
        else:
            new_account = st.text_input("**账户邮箱**", value="", help="账户邮箱，用于标识备注，可为空", placeholder="账户邮箱，仅用于自我备注，可为空！")
            new_access_token = st.text_input("**AC_Token***", help="AC_Token，刷新时的重要Token，不可为空", placeholder="AC_Token，刷新时的重要Token，不可为空！")
            new_refresh_token = st.text_input("**RF_Token**", help="RF_Token，AC刷新的重要Token，可为空，为空则刷新功能不可用", placeholder="RF_Token，AC刷新的重要Token！若无，可为空！")
        st.write("")
        if st.button("**新增账户**", use_container_width=True, type=button_type, key="new_account_button"):
            if new_group in accounts.keys():
                st.error("**此用户组已存在，请重新命名！**", icon=":material/error:")
            elif new_group == "":
                st.error("**用户组不可为空，请重新填写！**", icon=":material/error:")
            elif new_access_token == "":
                st.error("**SE_Token / AC_Token不可为空，请重新填写！**", icon=":material/error:")
            else:
                accounts[new_group] = {
                    "service_provider": new_service_provider,
                    "account_type": new_account_type,
                    "account": new_account,
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                }
                with open(current_path + "accounts.json", "w", encoding="utf-8") as file:
                    json.dump(accounts, file, indent=2)
                logger.info(f"【管理员】 新增了 {new_service_provider} 的账户 {new_group}！")
                st.session_state.add = True
                st.rerun()


    @st.experimental_dialog("生成邀请令牌")
    def new_invite():
        auto_it_gen = st.checkbox("**批量生成令牌**")
        it_token = ""
        if auto_it_gen:
            num_it_gen = st.number_input("**生成数量**", value=5, min_value=1, max_value=100, step=5)
            len_it_gen = st.number_input("**邀请令牌长度**", value=16, min_value=16, max_value=32)
        else:
            it_token = st.text_input("**邀请令牌**", placeholder="it-xxxxxxxxxxxxxxxx")
        col1, col2 = st.columns(2)
        with col1:
            it_openai_group = st.selectbox("**分配 OpenAI 用户组**", openai_list, index=0)
            it_openai = st.selectbox("**允许 ChatGPT**", [True, False], index=0)
        with col2:
            it_anthropic_group = st.selectbox("**分配 Anthropic 用户组**", anthropic_list, index=0)
            it_claude = st.selectbox("**允许 Claude**", [True, False], index=0)
        note = st.text_input("**备注**", placeholder="2024/06/30 00:00:00", help="备注信息，可为空")
        st.write("")
        with st.expander("**更多参数设置**", expanded=False):
            st.write("")
            it_site_limit = st.text_input("**限制网站**", value="", help="限制的网站, 为空则不限制", placeholder="限制的网站, 为空则不限制")
            col1, col2 = st.columns(2)
            with col1:
                it_expires_in = st.number_input("**过期时间（秒）**", value=0, help="token有效期（单位为秒），填 0 则永久有效")
                it_show_conversations = st.selectbox("**会话无需隔离**", ['true', 'false'], index=['true', 'false'].index("true"), help="false为隔离会话")
            with col2:
                it_gpt35_limit = st.number_input("**GPT-3.5限制**", value=-1, help="GPT-3.5对话限制，填 -1 则不限制")
                it_gpt4_limit = st.number_input("**GPT-4限制**", value=-1, help="GPT-4对话限制，填 -1 则不限制")
        st.write("")
        if st.button("**生成邀请令牌**", use_container_width=True, key="new_invite_token_gen", type=button_type):
            if it_token is None or it_token == "" and not auto_it_gen:
                st.error("**邀请令牌不能为空，请重新填写！**", icon=":material/error:")
            elif it_token in invite_config.keys() and not auto_it_gen:
                st.error("**此邀请令牌已存在，请重新填写！**", icon=":material/error:")
            elif auto_it_gen:
                for i in range(num_it_gen):
                    it_token = "it-" + secrets.token_urlsafe(len_it_gen)
                    invite_config[it_token] = {
                        "openai-group": it_openai_group,
                        "chatgpt": it_openai,
                        "anthropic-group": it_anthropic_group,
                        "claude": it_claude,
                        "note": note,
                        "used": False,
                        "site_limit": it_site_limit,
                        "expires_in": it_expires_in,
                        "gpt35_limit": it_gpt35_limit,
                        "gpt4_limit": it_gpt4_limit,
                        "show_conversations": it_show_conversations,
                        "claude_limit": "",
                        "expires_in_claude": "",
                        "show_conversations_claude": ""
                    }
                    logger.info(f"【管理员】 生成了新的邀请令牌 {it_token}！")
                with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                    json.dump(invite_config, f, indent=2)

                st.session_state.add = True
                st.rerun()
            else:
                invite_config[it_token] = {
                    "openai-group": it_openai_group,
                    "chatgpt": it_openai,
                    "anthropic-group": it_anthropic_group,
                    "claude": it_claude,
                    "note": note,
                    "used": False,
                    "site_limit": it_site_limit,
                    "expires_in": it_expires_in,
                    "gpt35_limit": it_gpt35_limit,
                    "gpt4_limit": it_gpt4_limit,
                    "show_conversations": it_show_conversations,
                    "claude_limit": "",
                    "expires_in_claude": "",
                    "show_conversations_claude": ""
                }
                with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                    json.dump(invite_config, f, indent=2)
                logger.info(f"【管理员】 生成了新的邀请令牌 {it_token}！")
                st.session_state.add = True
                st.rerun()


    @st.experimental_dialog("状态刷新")
    def refresh_user():
        st.write("")
        st.write("**账户状态检测**")
        col1, col2 = st.columns([0.8, 0.2])
        with col2:
            if st.checkbox("全选", key="all"):
                default = list(openai_data.keys())
            else:
                default = []
        with col1:
            status_list = st.multiselect("检测用户", list(openai_data.keys()), default=default, key="status_list", label_visibility="collapsed")

        sc_list = []
        er_list = []
        if "er_list" not in st.session_state:
            st.session_state.er_list = []
        if st.button("**状态检测**", use_container_width=True, key="check_user_account", type=button_type):
            if len(status_list) != 0:
                for user in status_list:
                    status = check_sharetoken(openai_data[user]["token"])
                    if status:
                        sc_list.append(user)
                    else:
                        er_list.append(user)
                if len(er_list) == 0:
                    logger.info(f"【管理员】 检测到所有账户状态正常！")
                    st.success("**所有账户状态正常！**", icon=":material/check_circle:")
                else:
                    st.info("滚动查看完整表格", icon=":material/double_arrow:")
                    df_result = pd.DataFrame({"成功": pd.Series(sc_list), "失败": pd.Series(er_list)})
                    st.data_editor(df_result, hide_index=True, use_container_width=True, height=143)
                    st.session_state.er_list = er_list
            else:
                st.error("**请先选择用户组，再进行状态检测！**", icon=":material/error:")

        st.divider()
        st.write("**需要刷新的账户**")
        user_group = st.multiselect("刷新的用户", st.session_state.er_list, key="user_groups", label_visibility="collapsed")
        if st.button("**刷新状态**", use_container_width=True, type=button_type):
            if len(user_group) != 0:
                for user in user_group:
                    status, name, token_key = get_sharetoken(
                        user,
                        accounts[openai_data[user]["group"]]["access_token"],
                        openai_data[user]["site_limit"],
                        openai_data[user]["expires_in"],
                        openai_data[user]["gpt35_limit"],
                        openai_data[user]["gpt4_limit"],
                        openai_data[user]["show_conversations"])
                    if status:
                        openai_data[user]["token"] = token_key
                        with open(current_path + '/openai.json', 'w', encoding='utf-8') as file:
                            json.dump(openai_data, file, indent=2)
                        logger.info(f"【管理员】 {name} 的 SA 刷新成功！")
                        st.success(f"**{user} 刷新成功！**", icon=":material/check_circle:")
                    else:
                        logger.error(f"【管理员】 {name} 的 SA 刷新失败，请检查 AC 是否失效！")
                        st.error(f"**{user} 刷新失败！**", icon=":material/error:")
            else:
                st.error("**请先刷新，然后选择需要刷新的用户组！**", icon=":material/error:")


    @st.experimental_dialog("生成刷新令牌")
    def new_refresh():
        auto_rf_gen = st.checkbox("**批量生成**")
        rf_token = ""
        if auto_rf_gen:
            num_rf_gen = st.number_input("**生成数量**", value=5, min_value=1, max_value=100, step=5, key="num_rf_gen_new")
            len_rf_gen = st.number_input("**刷新令牌长度**", value=16, min_value=16, max_value=32, key="len_rf_gen_new")
        else:
            rf_token = st.text_input("**刷新令牌**", key="rf_token_new", placeholder="rf-xxxxxxxxxxxxxxxx")
        col1, col2 = st.columns(2)
        with col1:
            rf_group = st.selectbox("**用户组别**", accounts.keys(), key="rf_group_new")
            site_limit = st.text_input("**限制网站（为空不限制）**", value="", help="限制的网站, 为空则不限制", key="site_limit_new", placeholder="限制网站, 为空则不限制")
            expires_in = st.number_input("**有效期（秒**）", value=0, help="token有效期（单位为秒），填 0 则永久有效", key="expires_in_new")
        with col2:
            gpt35_limit = st.number_input("**限制GPT-3.5次数**", value=-1, help="GPT-3.5对话限制，填 -1 则不限制", key="gpt35_limit_new")
            gpt4_limit = st.number_input("**限制GPT-4次数**", value=-1, help="GPT-4对话限制，填 -1 则不限制",  key="gpt4_limit_new")
            show_conversations = st.selectbox("**会话无需隔离**", ['true', 'false'], index=1, help="false为隔离会话", key="show_conversations_new")
        note = st.text_input("**备注**", help="备注信息，可为空", key="note_new", placeholder="2024/06/30 00:00:00")

        st.write("")
        if st.button("**生成刷新令牌**", use_container_width=True, key="new_refresh", type=button_type):
            if rf_token is None or rf_token == "" and not auto_rf_gen:
                st.error("**刷新令牌不能为空，请重新填写！**", icon=":material/error:")
            elif rf_token in refresh_data.keys() and not auto_rf_gen:
                st.error("**此刷新令牌已存在，请重新填写！**", icon=":material/error:")
            elif auto_rf_gen:
                for i in range(num_rf_gen):
                    rf_token = "rf-" + secrets.token_urlsafe(len_rf_gen)
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
                    logger.info(f"【管理员】 生成了新的刷新令牌：{rf_token}！")
                with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                    json.dump(refresh_data, f, indent=2)
                st.session_state.add = True
                st.rerun()
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
                st.session_state.add = True
                st.rerun()


    with st.sidebar:
        sidebar_html = sidebar_html.replace("#ffffff", "#f0f2f6")
        sidebar_html = sidebar_html.replace("#efede4", "#ffffff")
        st.markdown(sidebar_html, unsafe_allow_html=True)
        st.write("# 欢迎，" + web_setting["web"]["super_user"] + "！")
        st.divider()
        set_choose = sac.menu([
            sac.MenuItem('服务总览', icon='bar-chart-line-fill'),
            sac.MenuItem('域名管理', icon='router-fill'),
            sac.MenuItem('主题样式', icon='transparency'),
            sac.MenuItem('号池管理', icon='box-seam-fill', children=[
                sac.MenuItem('账号总览', icon='diagram-3'),
                sac.MenuItem('邀请令牌', icon='clipboard2-plus'),
                sac.MenuItem('刷新令牌', icon='bootstrap-reboot')]),
            sac.MenuItem('用户管理', icon='person-fill-gear', children=[
                sac.MenuItem('用户总览', icon='people'),
                sac.MenuItem('Oaifree', icon='airplane'),
                sac.MenuItem('Fuclaude', icon='archive')]),
            sac.MenuItem('更多功能', icon='basket2-fill', children=[
                sac.MenuItem('共享服务', icon='share'),
                sac.MenuItem('Oai-API', icon='database'),
                sac.MenuItem('关于项目', icon='info-circle')]),
        ], open_all=False)
        st.divider()
        if st.button("**返回首页**"):
            st.switch_page("home.py")
        if st.button("**退出登录**"):
            del st.session_state.role
            st.rerun()

    if set_choose == '服务总览':
        if web_setting["web"]["super_key"] == "12345678":
            key()

        with st.container(border=True):
            st.write("")
            st.write("##### 服务统计")
            st.write("")

            user_names = openai_data.keys()
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
            col1.metric("**用户数量**", len(user_names), len(user_names))
            col2.metric("**号池总计**", len(accounts.keys()), len(accounts.keys()))
            col3.metric("**服务次数**", st.session_state.count_people, st.session_state.count_people)
            col4.metric("**日志缓存**", size1, size_bytes1 - 36)
            col5.metric("**配置占用**", size2, size_bytes2 - 5131)

            st.divider()
            st.write('##### 图表数据')
            st.write("")
            with open(current_path + 'app.log', 'r', encoding='utf-8') as file:
                logs = file.read()

            pattern_user = re.compile(
                r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【用户登录】 用户：(\w+) 登录成功！')
            pattern_share = re.compile(
                r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【Share登录】 共享账户：(\w+) 登录成功！')
            pattern_sign = re.compile(
                r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【用户注册】 新用户：(\w+) 注册成功！')

            matches_user = pattern_user.findall(logs)
            matches_share = pattern_share.findall(logs)
            matches_sign = pattern_sign.findall(logs)

            all_dates = [datetime.strptime(date, '%Y-%m-%d %H').date() for date, _ in
                         matches_user + matches_share + matches_sign]
            min_date = min(all_dates) if all_dates else datetime.today().date()
            max_date = max(all_dates) if all_dates else datetime.today().date()

            with st.expander("**绘图工具**", expanded=False, icon=":material/square_foot:"):
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

                    if st.button("**保存设置**", use_container_width=True, type=button_type):
                        web_setting["chart"]["start_date"] = start_date
                        web_setting["chart"]["end_date"] = end_date
                        web_setting["chart"]["height"] = height
                        web_setting["chart"]["horizontal"] = horizontal
                        with open(current_path + "/setting.toml", "w", encoding="utf-8") as f:
                            toml.dump(web_setting, f)
                        st.toast("**更改设置成功！**", icon=":material/check_circle:")

                plot_choose = sac.segmented(
                    items=[
                        sac.SegmentedItem(label='登录统计', icon='bar-chart-line'),
                        sac.SegmentedItem(label='用户服务', icon='person-video3'),
                        sac.SegmentedItem(label='共享服务', icon='share'),
                        sac.SegmentedItem(label='注册人数', icon='door-open'),
                        sac.SegmentedItem(label='时段统计', icon='database-fill-check'),
                    ], use_container_width=True, size='sm', radius='sm', color='dark')

            st.write("")
            data_user = pd.DataFrame(matches_user, columns=['日期时间', 'user'])
            data_share = pd.DataFrame(matches_share, columns=['日期时间', 'user'])
            data_sign = pd.DataFrame(matches_sign, columns=['日期时间', 'user'])

            data_user['日期'] = pd.to_datetime(data_user['日期时间']).dt.date
            data_share['日期'] = pd.to_datetime(data_share['日期时间']).dt.date
            data_sign['日期'] = pd.to_datetime(data_sign['日期时间']).dt.date

            filtered_user = data_user[(data_user['日期'] >= start_date) & (data_user['日期'] <= end_date)]
            filtered_share = data_share[(data_share['日期'] >= start_date) & (data_share['日期'] <= end_date)]
            filtered_sign = data_sign[(data_sign['日期'] >= start_date) & (data_sign['日期'] <= end_date)]

            if plot_choose == '登录统计':
                if not filtered_user.empty or not filtered_share.empty:
                    st.markdown(
                        '<div style="text-align: center; font-weight: bold; font-size: 20px;">登录统计总览图</div>',
                        unsafe_allow_html=True)
                    st.write("")
                    matches = pd.concat([filtered_user, filtered_share])
                    st.session_state.count_people = len(matches)
                    matches['日期'] = matches['日期'].astype(str)
                    summary = matches.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
                else:
                    st.write("")
                    st.info("""
                    
                    **暂无相关数据**
                    
                    **快去首页使用吧！**
                    
                    """, icon=':material/double_arrow:')
            if plot_choose == '用户服务':
                if not filtered_user.empty:
                    st.markdown(
                        '<div style="text-align: center; font-weight: bold; font-size: 20px;">用户服务统计图</div>',
                        unsafe_allow_html=True)
                    st.write("")
                    filtered_user['日期'] = filtered_user['日期'].astype(str)
                    summary = filtered_user.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
                else:
                    st.write("")
                    st.info("""

                    **暂无相关数据**

                    **快去首页使用吧！**

                    """, icon=':material/double_arrow:')
            if plot_choose == '共享服务':
                if not filtered_share.empty:
                    st.markdown(
                        '<div style="text-align: center; font-weight: bold; font-size: 20px;">共享服务统计图</div>',
                        unsafe_allow_html=True)
                    st.write("")
                    filtered_share['日期'] = filtered_share['日期'].astype(str)
                    summary = filtered_share.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                    st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
                else:
                    st.write("")
                    st.info("""

                    **暂无相关数据**

                    **快去首页使用吧！**

                    """, icon=':material/double_arrow:')
            if plot_choose == '注册人数':
                if not filtered_sign.empty:
                    st.markdown(
                        '<div style="text-align: center; font-weight: bold; font-size: 20px;">注册人数统计图</div>',
                        unsafe_allow_html=True)
                    st.write("")
                    filtered_sign['日期'] = filtered_sign['日期'].astype(str)
                    summary = filtered_sign.groupby(['日期', 'user']).size().reset_index(name='注册总计')
                    pivot_table = summary.pivot(index='日期', columns='user', values='注册总计').fillna(0)
                    st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
                else:
                    st.write("")
                    st.info("""

                    **暂无相关数据**

                    **快去首页使用吧！**

                    """, icon=':material/double_arrow:')
            if plot_choose == '时段统计':
                if not filtered_user.empty:
                    st.markdown(
                        '<div style="text-align: center; font-weight: bold; font-size: 20px;">时段人数统计图</div>',
                        unsafe_allow_html=True)
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
                    st.info("""

                    **暂无相关数据**

                    **快去首页使用吧！**

                    """, icon=':material/double_arrow:')

            st.divider()
            st.write("##### 站点迁移")
            st.write("")
            st.warning("""

            **仅支持 V1.2.0 版本后的配置文件导入！**

            **由于最新版本 V1.2.0 的配置文件进行了重构，请慎重上传 V1.1.x 或 更早版本 的配置文件！**

            """, icon=':material/sd_card_alert:')

            with open(current_path + 'app.log', 'r', encoding='utf-8') as file:
                lines = file.readlines()
            st.write("")
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                if st.button("**导出配置**", use_container_width=True, type=button_type):
                    download()
            with col2:
                if st.button("**导入配置**", use_container_width=True, type=button_type):
                    upload()

            st.divider()
            st.write("##### 运行日志")
            st.write("")

            lines.reverse()
            result_str = "".join(str(line) for line in lines)
            st.text_area("运行日志", value=result_str, height=300, label_visibility="collapsed")
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                st.write("")
                if st.button("**清理日志**", use_container_width=True, type=button_type):
                    log_content = "【OaiT服务已成功开启！】\n"
                    with open(current_path + "/app.log", "w", encoding="utf-8") as log_file:
                        log_file.write(log_content)
                    st.session_state.success = True
                    st.rerun()
            st.write("")
    if set_choose == '域名管理':
        if not web_setting["web"]["readme"]:
            readme()

        with st.container(border=True):
            st.write("")
            st.write("##### 域名列表")
            st.write("")
            st.info("**Fuclaude 指向 claude UI， Oiafree 指向 ChatGPT UI， Pandora 指向 Pandora 经典UI**",
                    icon=':material/double_arrow:')
            st.write("")
            rows = [[datas['name'], name, datas['speed'], datas['type']] for name, datas in domain_data.items()]
            df0 = pd.DataFrame(rows, columns=["名称", "服务域名", "延迟", "类型"])
            data = st.data_editor(df0, hide_index=True, use_container_width=True, height=248, num_rows="dynamic", disabled=["延迟"], column_config={"类型": st.column_config.SelectboxColumn(options=["Fuclaude", "Oaifree", "Pandora"])})

            st.write("")
            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                if st.button("**保存更改**", use_container_width=True, key="save_domain", type=button_type):
                    st.session_state.change_domain = True
                    json_data = data.to_dict('records')
                    json_data = {str(record['服务域名']): {
                        'name': record['名称'],
                        'speed': record['延迟'],
                        'type': record['类型']
                    } for record in json_data}
                    json.dumps(json_data, indent=2)
                    with open(current_path + "domain.json", "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=2)
                    st.session_state.success = True
                    st.rerun()
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
                            'name': record['名称'],
                            'speed': i,
                            'type': record['类型']
                        }
                    with open(current_path + "domain.json", "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=2)
                    st.session_state.test = True
                    st.rerun()
            with col8:
                if st.button("**新增域名**", use_container_width=True, type=button_type):
                    add_domain()

            st.divider()
            st.write("##### 服务设置")
            st.write("")
            openai_domain = ["不启用"]
            anthropic_domain = ["不启用"]
            for domain in df0["服务域名"].tolist():
                if domain_data[domain]["type"] == "Fuclaude":
                    anthropic_domain.append(domain)
                else:
                    openai_domain.append(domain)

            choose_domain = st.selectbox("**允许用户自由选择服务域名**", ["允许", "不允许"], index=["允许", "不允许"].index(web_setting["domain"]["choose_domain"]))

            if choose_domain == "不允许":
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        domain_default_openai = st.selectbox("**默认 OpenAI 服务域名**", openai_domain, index=openai_domain.index(web_setting["domain"]["domain_default_openai"]))
                    except:
                        domain_default_openai = st.selectbox("**默认 OpenAI 服务域名**", openai_domain, key="domain_default_openai")
                        if "change_domain" in st.session_state:
                            st.write("")
                            st.error("**警告：由于您修改了域名信息导致设置冲突！请尽快重新设置默认服务设置！**",
                                     icon=':material/error:')
                            st.write("")
                            st.toast("**警告：由于您修改了域名信息导致设置冲突！请重新设置默认服务设置！**",
                                     icon=':material/error:')
                with col2:
                    try:
                        domain_default_anthropic = st.selectbox("**默认 Anthropic 服务域名**", anthropic_domain, index=anthropic_domain.index(web_setting["domain"]["domain_default_anthropic"]))
                    except:
                        domain_default_anthropic = st.selectbox("**默认 Anthropic 服务域名**", anthropic_domain, key="domain_default_anthropic")
                        if "change_domain" in st.session_state:
                            st.write("")
                            st.error("**警告：由于您修改了域名信息！请重新设置默认服务！**", icon=':material/error:')
                            st.write("")
                            st.toast("**警告：由于您修改了域名信息！请重新设置默认服务！**", icon=':material/error:')
            else:
                try:
                    user_domain = st.multiselect("**用户使用的服务域名**", df0["服务域名"].tolist(), default=web_setting["domain"]["domain_select"])
                except:
                    if "change_domain" in st.session_state:
                        st.write("")
                        st.error("**警告：由于您修改了域名信息导致设置冲突！请尽快重新设置默认服务设置！**", icon=':material/error:')
                        st.write("")
                        st.toast("**警告：由于您修改了域名信息导致设置冲突！请重新设置默认服务设置！**", icon=':material/error:')
                    user_domain = st.multiselect("**用户可使用的服务域名**", df0["服务域名"].tolist(), key="user_domain")

            st.write("")
            col1, col2 = st.columns([0.2, 0.8])

            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_domain_setting2", type=button_type):
                    web_setting["domain"]["choose_domain"] = choose_domain
                    if "change_domain" in st.session_state:
                        del st.session_state.change_domain
                    if choose_domain == "不允许":
                        web_setting["domain"]["domain_default_openai"] = domain_default_openai
                        web_setting["domain"]["domain_default_anthropic"] = domain_default_anthropic
                        with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                            toml.dump(web_setting, f)
                        st.session_state.success = True
                        st.rerun()
                    else:
                        if len(user_domain) == 0:
                            st.toast("**允许用户使用的域名不能为空！**", icon=':material/error:')
                            st.stop()
                        else:
                            web_setting["domain"]["domain_select"] = user_domain
                        with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                            toml.dump(web_setting, f)
                        logger.info(f"【管理员】 修改了服务域名设置！")
                        st.session_state.success = True
                        st.rerun()
                st.write("")
    if set_choose == '主题样式':
        if not web_setting["web"]["readme"]:
            readme()

        with st.container(border=True):
            st.write("")
            st.write("##### 网站设置")
            st.write("")

            col1, col2 = st.columns(2)
            with col1:
                super_user = st.text_input("**管理员昵称**", value=web_setting["web"]["super_user"])
            with col2:
                super_key = st.text_input("**管理员密钥**", value=web_setting["web"]["super_key"], type="password")

            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("**站点标题**", value=web_setting["web"]["title"])
            with col2:
                subtitle = st.text_input("**站点副标题**", value=web_setting["web"]["subtitle"])

            col1, col2 = st.columns(2)
            with col1:
                login_theme = st.selectbox("**登录主题**", ["Simple White", "Classic Black", "Retro Orange"], index=["Simple White", "Classic Black", "Retro Orange"].index(web_setting["web"]["login_theme"]))
            with col2:
                sidebar_state = st.selectbox("**侧边栏展开**", ["auto", "expanded", "collapsed"], index=["auto", "expanded", "collapsed"].index(web_setting["web"]["sidebar_state"]))
            st.write("")
            col6, col7, col8 = st.columns([0.2, 0.2, 0.6])
            with col6:
                if st.button("**保存更改**", use_container_width=True, key="save_setting_web", type=button_type):
                    if super_key == "" or super_user == "":
                        st.toast("**管理员昵称和密钥不能为空！**", icon=':material/error:')
                    elif len(super_key) < 8:
                        st.toast("**管理员密钥长度不能小于8位！**", icon=':material/error:')
                    elif super_key == "12345678":
                        st.toast("**管理员密钥不能为默认值！**", icon=':material/error:')
                    else:
                        web_setting["web"]["super_user"] = super_user
                        web_setting["web"]["super_key"] = super_key
                        web_setting["web"]["login_theme"] = login_theme
                        web_setting["web"]["sidebar_state"] = sidebar_state
                        web_setting["web"]["title"] = title
                        web_setting["web"]["subtitle"] = subtitle
                        with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                            toml.dump(web_setting, f)
                        logger.info(f"【管理员】 修改了网站设置！")
                        st.session_state.success = True
                        st.rerun()

            st.divider()
            st.write("##### 公告设置")
            st.write("")

            if login_theme == "Retro Orange":
                st.info("**Retro Orange 主题下的公告支持 Html 语法，显示在登录页面最下方！**", icon=':material/double_arrow:')
                st.write("")
                html = st.text_area("**公告内容**", value=web_setting['web']['Retro_Orange_notice'], height=400)
            else:
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

            st.write("")
            col6, col7 = st.columns([0.2, 0.8])
            with col6:
                if st.button("**保存更改**", use_container_width=True, key="save_notice", type=button_type):
                    if login_theme == "Retro Orange":
                        web_setting["web"]["Retro_Orange_notice"] = html
                    else:
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
                    st.session_state.success = True
                    st.rerun()
                st.write("")

            if login_theme != "Retro Orange":
                st.divider()

                st.write("##### 公告预览")
                st.write("")
                st.write("")
                col1, col2, col3 = st.columns([0.15, 0.7, 0.15])
                with col2:
                    sac.alert(label=notice_title, description=notice_subtitle, color=notice_color, banner=notice_banner, variant=notice_style, size=notice_size, radius=notice_radius)
                st.write("")
                st.write("")
    if set_choose == '账号总览':
        with st.container(border=True):
            st.write("")
            st.write("##### 号池列表")
            st.warning("""
            **用户组 是每个账号的唯一标识，是各个模块相互联系的重要关键字，不允许 名称 相同!**
            
            **注：Anthropic 无 RF_Token ，只需在 AC_Token 内填入 Claude 的 Session-Token 即可。**
            """, icon=':material/sd_card_alert:')
            st.write("")

            fields = ['用户组', '服务商', '订阅类型', '账户邮箱', 'AC_Token', 'RF_Token']
            rows = [[groups, datas['service_provider'], datas['account_type'], datas['account'], datas['access_token'],
                     datas['refresh_token']] for groups, datas in accounts.items()]
            df1 = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                order = st.multiselect("**数据显示**", fields, web_setting["excel"]["order_account"], key="order_account")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_account"]), key="hide_index_account")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_account"], min_value=100, max_value=1000, step=100, key="height_account")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_account"]), key="order_what_account")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index(web_setting["excel"]["order_row_account"]), key="order_row_account")

                if order_row == "升序":
                    df1 = df1.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df1 = df1.sort_values(by=order_what, ascending=False)

            edited_df1 = st.data_editor(df1, hide_index=hide_index, use_container_width=True, num_rows="dynamic", height=height, column_config={
                    "服务商": st.column_config.SelectboxColumn(options=["OpenAI", "Anthropic"]),
                    "订阅类型": st.column_config.SelectboxColumn(options=["Free", "Plus"])}, column_order=order)

            st.write("")
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
                    st.session_state.success = True
                    st.rerun()
            with col7:
                if st.button("**新增账户**", use_container_width=True, type=button_type):
                    new_account()
            with col8:
                st.link_button("**获取 RF**", "https://token.oaifree.com/auth", use_container_width=True, type=button_type)

            st.divider()
            st.write("##### 刷新 AC_Token (Oaifree)")
            st.warning("""**必须配置 RF_Token 后，此自助程序才能正常生效！**""", icon=':material/sd_card_alert:')
            st.info("""
            **已对时间有限 （ expires_in不为0 ） 的用户进行单独优化，开启后不会影响并重置此类用户的使用剩余时间！**
            """, icon=':material/double_arrow:')

            st.info("""
            **开启后，用户登陆 / 共享站登录时会自动检测用户的 SA_Token**
            
            **当状态获取失败时，程序会自动尝试刷新 SA_Token 和 AC_Token，实现号池状态刷新自动化。**
            """, icon=':material/double_arrow:')

            st.write("")
            refresh = st.checkbox("**自动检测 SA/AC 状态**", value=web_setting["web"]["refresh_all"])
            st.write("")
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_AC_Token刷新", type=button_type):
                    web_setting["web"]["refresh_all"] = refresh
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    st.toast("**更改成功!**", icon=':material/check_circle:')

            st.divider()
            st.write("##### 手动刷新 AC_Token (Oaifree)")
            st.info("""
            **若无 RF_Token 可利用此方法 自行定期 手动刷新 AC_Token。**
            
            **注意：手动刷新并不会刷新用户登录的 SA_Token ，请前往用户总览检测用户状态并手动刷新！**
            """, icon=':material/double_arrow:')
            st.write("")
            group = st.selectbox("**选择刷新的用户组**", accounts.keys())
            st.write("")
            col1, col2 = st.columns([0.2, 0.8])
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button(f"**刷新此用户组**", use_container_width=True, type=button_type):
                    status, new_access_token = get_accesstoken(accounts[group]['refresh_token'])
                    if status:
                        st.toast(f"**刷新 {group} 成功！**", icon=':material/check_circle:')
                        logger.info(f"【管理员】 成功刷新了 {group} 的 AC_Token！")
                        accounts[group]['access_token'] = new_access_token
                        with open(current_path + "accounts.json", "w", encoding="utf-8") as f:
                            json.dump(accounts, f, indent=2)
                    else:
                        with col6:
                            logger.info(f"【管理员】 刷新 {group} 失败！请检查对应的 RF_Token 是否失效！")
                            st.toast(f"**刷新 {group} 失败！**", icon=':material/error:')
    if set_choose == '邀请令牌':
        with st.container(border=True):
            st.write("")
            st.write("##### 邀请令牌")
            st.info("""
            **OpenAI_用户组 规定被分配的 OpenAI 用户组别， Anthropic_用户组 规定被分配的 Anthropic 用户组别。**
            
            **ChatGPT 若勾选表示可使用 ChatGPT服务， Claude 若勾选表示可使用 Claude 服务。**
            
            **是否使用 表示此令牌是否已被使用，单个令牌只允许使用一次。**
            """, icon=':material/double_arrow:')
            st.write("")
            fields = ['Invite_Token', 'OpenAI_用户组', 'ChatGPT', 'Anthropic_用户组', 'Claude', '备注', '是否使用', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离', '限制网站-claude', '过期秒数-claude', '会话无需隔离-claude']
            rows = [[IV_Token, invite_config[IV_Token]["openai-group"], invite_config[IV_Token]["chatgpt"],
                     invite_config[IV_Token]["anthropic-group"], invite_config[IV_Token]["claude"],
                     invite_config[IV_Token]["note"], invite_config[IV_Token]["used"], invite_config[IV_Token]["site_limit"],
                     invite_config[IV_Token]["expires_in"], invite_config[IV_Token]["gpt35_limit"], invite_config[IV_Token]["gpt4_limit"],
                     invite_config[IV_Token]["show_conversations"], invite_config[IV_Token]["claude_limit"], invite_config[IV_Token]["expires_in_claude"],
                     invite_config[IV_Token]["show_conversations_claude"]] for IV_Token, Group in invite_config.items()]
            df3 = pd.DataFrame(rows, columns=fields)

            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                col1, col2 = st.columns([0.75, 0.25])
                with col1:
                    order = st.multiselect("**显示数据**", fields, web_setting["excel"]["order_invite"], key="order")
                with col2:
                    st.write("")
                    if st.button("**删除已用**", use_container_width=True, key="delete_invite", type=button_type):
                        for i in list(invite_config.keys()):
                            if invite_config[i]["used"]:
                                invite_config.pop(i)
                        with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                            json.dump(invite_config, f, indent=2)
                        logger.info(f"【管理员】 删除了已使用的邀请令牌！")
                        st.session_state.delete = True
                        st.rerun()
                    if st.button("**删除所有**", use_container_width=True, key="delete_all_invite", type=button_type):
                        invite_config.clear()
                        with open(current_path + "invite.json", "w", encoding="utf-8") as f:
                            json.dump(invite_config, f, indent=2)
                        logger.info(f"【管理员】 删除了所有邀请令牌！")
                        st.session_state.delete = True
                        st.rerun()

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_invite"]), key="hide_index_invite")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_invite"], min_value=100, max_value=1000, step=100, key="height_invite")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_invite"]), key="order_what")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index(web_setting["excel"]["order_row_invite"]), key="order_row")

                if order_row == "升序":
                    df3 = df3.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df3 = df3.sort_values(by=order_what, ascending=False)

            edited_df = st.data_editor(df3, hide_index=hide_index, use_container_width=True, height=height, column_order=order, num_rows="dynamic", column_config={
                    "OpenAI_用户组": st.column_config.SelectboxColumn(options=openai_list),
                    "Anthropic_用户组": st.column_config.SelectboxColumn(options=anthropic_list)}, disabled=["是否使用"])
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_invite", type=button_type):
                    web_setting["excel"]["hide_index_invite"] = hide_index
                    web_setting["excel"]["height_invite"] = height
                    web_setting["excel"]["order_what_invite"] = order_what
                    web_setting["excel"]["order_row_invite"] = order_row
                    web_setting["excel"]["order_invite"] = order
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    json_data = df_to_json_invite(edited_df)
                    with open(current_path + 'invite.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data)
                    st.session_state.success = True
                    st.rerun()
            with col2:
                if st.button("**生成令牌**", use_container_width=True, key="new_invite_token", type=button_type):
                    new_invite()

            st.divider()
            st.write("##### 自助服务")
            st.write("")
            invite_link_enable = st.checkbox("**显示自助发卡平台链接**", value=web_setting["web"]["invite_link_enable"], key="invite_link_enable")
            invite_link = st.text_input("**平台链接**", value=web_setting["web"]["invite_link"], key="invite_link", label_visibility="collapsed")
            st.write("")
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_invite_link", type=button_type):
                    web_setting["web"]["invite_link_enable"] = invite_link_enable
                    web_setting["web"]["invite_link"] = invite_link
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    logger.info(f"【管理员】 修改了邀请令牌自助服务！")
                    st.toast("**更改成功!**", icon=':material/check_circle:')
            st.write("")
    if set_choose == '刷新令牌':
        with st.container(border=True):
            st.write("")
            st.write("##### 账户续费")
            st.info("""**开启后将允许过期用户在 首页-账户续费 页面内续费，您可设置不同类型的令牌来决定这些用户的续费时间。**""", icon=':material/double_arrow:')
            user_refresh = st.checkbox("**开启续费功能**", value=web_setting["web"]["user_refresh"])
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_refresh1", type=button_type):
                    web_setting["web"]["user_refresh"] = user_refresh
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    st.toast("**更改成功!**", icon=':material/check_circle:')

            st.divider()
            st.write("##### 刷新令牌 - Oaifree")
            st.info("""**注：续费时间最多为 10 天（随AC_Token同步失效），若想更久，请将令牌的过期秒数设置为 0，升级为永不过期！**""", icon=':material/double_arrow:')
            st.write("")

            fields = ['userRF_Token', '用户组', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离', '备注', '是否使用']
            rows = [[rf_token] + list(datas.values()) for rf_token, datas in refresh_data.items()]
            df4 = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                st.write("")
                col1, col2 = st.columns([0.75, 0.25])
                with col1:
                    order = st.multiselect("**显示数据**", fields, web_setting["excel"]["order_refresh"], key="order_refresh")
                with col2:
                    if st.button("**删除已用令牌**", use_container_width=True, key="delete_refresh", type=button_type):
                        for i in list(refresh_data.keys()):
                            if refresh_data[i]["used"]:
                                refresh_data.pop(i)
                        with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                            json.dump(refresh_data, f, indent=2)
                        st.session_state.delete = True
                        st.rerun()
                    if st.button("**删除所有令牌**", use_container_width=True, key="delete_all_refresh", type=button_type):
                        refresh_data.clear()
                        with open(current_path + "refresh.json", "w", encoding="utf-8") as f:
                            json.dump(refresh_data, f, indent=2)
                        st.session_state.delete = True
                        st.rerun()

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_refresh"]), key="hide_index_refresh")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_refresh"], min_value=100, max_value=1000, step=100, key="height_refresh")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_refresh"]), key="order_what_refresh")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index( web_setting["excel"]["order_row_refresh"]), key="order_row_refresh")

                if order_row == "升序":
                    df4 = df4.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df4 = df4.sort_values(by=order_what, ascending=False)

            edited_df4 = st.data_editor(df4, hide_index=hide_index, use_container_width=True, height=height, num_rows="dynamic", disabled=["是否使用"], column_order=order, column_config={"用户组": st.column_config.SelectboxColumn(options=accounts.keys())})
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_refresh", type=button_type):
                    web_setting["web"]["user_refresh"] = user_refresh
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    json_data4 = df_to_json4(edited_df4)
                    with open(current_path + 'refresh.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data4)
                    st.session_state.success = True
                    st.rerun()
            with col2:
                if st.button("**生成令牌**", use_container_width=True, key="new_refresh_token", type=button_type):
                    new_refresh()

            st.divider()
            st.write("##### 刷新令牌 - Claude")
            st.write("")
            st.success("""**敬请期待...**""")

            st.divider()
            st.write("##### 自助服务")
            st.write("")
            refresh_link_enable = st.checkbox("**显示自助发卡平台链接**", value=web_setting["web"]["refresh_link_enable"], key="refresh_link_enable")
            refresh_link = st.text_input("**平台链接(完整网址)**", value=web_setting["web"]["refresh_link"], key="refresh_link", label_visibility="collapsed")
            st.write("")
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_refresh_link", type=button_type):
                    web_setting["web"]["refresh_link_enable"] = refresh_link_enable
                    web_setting["web"]["refresh_link"] = refresh_link
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    st.toast("**更改成功！**", icon=':material/check_circle:')
            st.write("")
    if set_choose == '用户总览':
        with st.container(border=True):
            st.write("")
            st.write("##### 用户列表")
            st.info("""
            **所有表格均支持 搜索、下载、新建、删除、修改、排序 ，但请及时保存更改！**
            
            **UID是用户的唯一标识，可用于修改密码、账户登录，ChatGPT、Claude表示该用户是否可用。**
            """, icon=':material/double_arrow:')
            st.write("")
            fields = ['账户', '密码', 'UID', 'ChatGPT', 'Claude', '备注']
            rows = [[user, datas['password'], datas['uid'], datas['allow_chatgpt'], datas['allow_claude'], datas['note']] for user, datas in user_data.items()]
            df = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                order = st.multiselect("**数据显示**", fields, web_setting["excel"]["order_user"], key="order_user")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_user"]), key="hide_index_user")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_user"], min_value=100, max_value=1000, step=100, key="height_user")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_user"]), key="order_what_user")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index(web_setting["excel"]["order_row_user"]), key="order_row_user")

                if order_row == "升序":
                    df = df.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df = df.sort_values(by=order_what, ascending=False)

            edited_df_user_data = st.data_editor(df, hide_index=hide_index, use_container_width=True, num_rows="dynamic", height=height, column_order=order, disabled=["UID"])
            st.write("")
            col1, col2 = st.columns([0.2, 0.8])
            col3, col4 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_user_data", type=button_type):
                    web_setting["excel"]["hide_index_user"] = hide_index
                    web_setting["excel"]["height_user"] = height
                    web_setting["excel"]["order_what_user"] = order_what
                    web_setting["excel"]["order_row_user"] = order_row
                    web_setting["excel"]["order_user"] = order
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    json_data = df_to_json_user_data(edited_df_user_data)
                    json_dict = json.loads(json_data)
                    users_to_delete = []
                    error = False
                    for user in json_dict.keys():
                        if user not in user_data.keys():
                            error = True
                    if not error:
                        for user in user_data.keys():
                            if user not in json_dict.keys():
                                users_to_delete.append(user)
                        for user in users_to_delete:
                            try:
                                del openai_data[user]
                            except:
                                pass
                            try:
                                del anthropic_data[user]
                            except:
                                pass
                        with open(current_path + '/openai.json', 'w', encoding='utf-8') as json_file:
                            json.dump(openai_data, json_file, ensure_ascii=False, indent=2)
                        with open(current_path + '/anthropic.json', 'w', encoding='utf-8') as json_file:
                            json.dump(anthropic_data, json_file, ensure_ascii=False, indent=2)
                        with open(current_path + '/users.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(json_data)
                        st.session_state.success = True
                        st.rerun()
                    else:
                        with col3:
                            st.error("**不允许在此表格内直接新增用户！请使用下方注册功能新增用户！**")
                            st.toast("**非法操作，请重试！**", icon=":material/error:")

            st.divider()
            st.write("##### 用户注册 - 管理员")
            st.write("")
            allow = st.checkbox("**本次允许用户重名（可用于变更 Claude/OpenAI 服务，注意：账号数据会被完全覆盖）**")
            col1, col2, col3 = st.columns(3)
            with col1:
                user_new_acc = st.text_input("**账户**", key="user_new_acc_admin", placeholder="user_name")
                user_new_pass = st.text_input("**密码**", key="user_new_pass_admin", type="password", placeholder="user_password")
            with col2:
                user_new_group_openai = st.selectbox("**分配OpenAI_组别**", openai_list)
                user_new_group_anthropic = st.selectbox("**分配Anthropic_组别**", anthropic_list)
            with col3:
                if user_new_group_openai:
                    user_allow_chatgpt = st.selectbox("**允许使用 ChatGPT**", [True, False], index=0)
                else:
                    user_allow_chatgpt = st.selectbox("**允许使用 ChatGPT**", [True, False], index=1, disabled=True)
                if user_new_group_anthropic:
                    user_allow_claude = st.selectbox("**允许使用 Claude**", [True, False], index=0)
                else:
                    user_allow_claude = st.selectbox("**允许使用 Claude**", [True, False], index=1, disabled=True)
            st.write("")
            with st.expander("**设置更多参数**", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    site_limit = st.text_input("限制网站（为空不限制）", value="", help="限制的网站, 为空则不限制", placeholder="site1,site2")
                    expires_in = st.number_input("过期秒数（秒）", value=0, help="token有效期（单位为秒），填 0 则永久有效")
                    show_conversations = st.selectbox("会话无需隔离", ['true', 'false'], index=1, help="false为隔离会话")
                with col2:
                    gpt35_limit = st.number_input("限制GPT-3.5", value=-1, help="GPT-3.5对话限制，填 -1 则不限制")
                    gpt4_limit = st.number_input("限制GPT-4", value=-1, help="GPT-4对话限制，填 -1 则不限制")
                    note = st.text_input("备注", placeholder="备注信息，可为空")
                uid = st.text_input("UID(4+32位，自动生成)", value="UID-" + secrets.token_urlsafe(32), help="用户的UID，自动生成，用于用户登录、修改密码", disabled=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**注册用户**", use_container_width=True, key="register_user_admin", type=button_type):
                    if not allow:
                        if user_new_acc in user_data:
                            with col6:
                                st.toast("**账户名称已存在!**", icon=":material/error:")
                                st.error("**账户名称已存在!**", icon=":material/error:")
                                st.stop()

                    if user_new_acc == "":
                        with col6:
                            st.toast("**请填写账户名称!**", icon=":material/error:")
                            st.error("**请填写账户名称!**", icon=":material/error:")
                    elif user_new_pass == "":
                        with col6:
                            st.toast("**请填写账户密码!**", icon=":material/error:")
                            st.error("**请填写账户密码!**", icon=":material/error:")
                    elif user_new_group_openai and user_allow_chatgpt:
                        ac_token = accounts[user_new_group_openai]['access_token']
                        status, new_name, new_token_key = get_sharetoken(user_new_acc, ac_token, site_limit, expires_in, gpt35_limit, gpt4_limit, show_conversations)
                        if status:
                            st.session_state.signup1 = True
                            json_data_2 = {
                                user_new_acc: {
                                    'token': new_token_key,
                                    'group': user_new_group_openai,
                                    'type': accounts[user_new_group_openai]['account_type'],
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
                        elif not user_allow_chatgpt:
                            for user in openai_data.keys():
                                if user == user_new_acc:
                                    del openai_data[user]
                        else:
                            with col6:
                                st.error(f"**新增失败，请检查 {user_new_group_openai} 的 AC_Token 状态！**", icon=":material/error:")
                    else:
                        st.session_state.signup1 = True

                    if user_new_group_anthropic and user_allow_claude and "signup1" in st.session_state:
                        json_data_3 = {
                            user_new_acc: {
                                'token': accounts[user_new_group_anthropic]['access_token'],
                                'group': user_new_group_anthropic,
                                'type': accounts[user_new_group_anthropic]['account_type']
                            }
                        }
                        anthropic_data.update(json_data_3)
                        anthropic_datas = json.dumps(anthropic_data, indent=2)
                        with open(current_path + 'anthropic.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(anthropic_datas)
                    elif not user_allow_claude:
                        for user in anthropic_data.keys():
                            if user == user_new_acc:
                                del anthropic_data[user]

                    if "signup1" in st.session_state:
                        json_data_1 = {
                            user_new_acc: {
                                'password': user_new_pass,
                                'uid': uid,
                                'allow_chatgpt': user_allow_chatgpt,
                                'allow_claude': user_allow_claude,
                                'note': note,
                            }
                        }
                        user_data.update(json_data_1)
                        user_data = json.dumps(user_data, indent=2)
                        with open(current_path + 'users.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(user_data)
                        del st.session_state.signup1
                        logger.info(f"【管理员】 注册了新用户 {user_new_acc}，OpenAI组别：{user_new_group_openai}，Anthropic组别：{user_new_group_anthropic}")
                        st.session_state.add = True
                        st.rerun()
            st.write("")
    if set_choose == 'Oaifree':
        with st.container(border=True):
            st.write("")
            st.write("##### Oaifree 镜像服务")
            st.write("")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("**用户总数**", len(openai_data))
            with col2:
                st.metric("**Free总数**", len([i for i in openai_data.values() if i['type'] == 'Free']))
            with col3:
                st.metric("**PLUS总数**", len([i for i in openai_data.values() if i['type'] == 'Plus']))
            st.info("**此部分可查看使用 Oaifree 服务的用户，仅支持更改SA_Token、删除 Oaifree 服务下的用户**")
            st.write("")
            fields = ['账户', 'SA_Token', '用户组', '订阅类型', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离']
            rows = [[user] + list(account.values()) for user, account in openai_data.items()]
            df = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                order = st.multiselect("**显示数据**", fields, web_setting["excel"]["order_oaifree"], key="order_oaifree")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_oaifree"]), key="hide_index_oaifree")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_oaifree"], min_value=100, max_value=1000, step=100, key="height_oaifree")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_oaifree"]), key="order_what_oaifree")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index(web_setting["excel"]["order_row_oaifree"]), key="order_row_oaifree")

                if order_row == "升序":
                    df = df.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df = df.sort_values(by=order_what, ascending=False)

            edited_df = st.data_editor(df, column_order=order, hide_index=hide_index, use_container_width=True, height=height, disabled=['账户', '用户组', 'UID', '订阅类型', '限制网站', '过期秒数', 'GPT3.5限制', 'GPT4限制', '会话无需隔离'], num_rows="dynamic")
            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存更改** ", use_container_width=True, key="save_user", type=button_type):
                    for user in openai_data.keys():
                        if user not in edited_df['账户']:
                            user_data[user]["allow_chatgpt"] = False
                            with open(current_path + 'users.json', 'w', encoding='utf-8') as json_file:
                                json_file.write(json.dumps(user_data, indent=2))
                    error = False
                    for user in edited_df['账户']:
                        if user not in user_data.keys():
                            error = True
                    if not error:
                        json_data = df_to_json_oaifree(edited_df)
                        web_setting["excel"]["hide_index_oaifree"] = hide_index
                        web_setting["excel"]["height_oaifree"] = height
                        web_setting["excel"]["order_what_oaifree"] = order_what
                        web_setting["excel"]["order_row_oaifree"] = order_row
                        web_setting["excel"]["order_oaifree"] = order
                        with open(current_path + '/setting.toml', 'w', encoding='utf-8') as f:
                            toml.dump(web_setting, f)
                        with open(current_path + '/openai.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(json_data)
                        st.session_state.success = True
                        st.rerun()
                    else:
                        with col6:
                            st.toast("**非法操作，请重试！**")
                            st.error("**不允许在此表格内直接新增用户！请使用注册功能 新增用户 或 变更用户状态！**")
            with col2:
                if st.button("**状态刷新**", use_container_width=True, type=button_type):
                    refresh_user()
            with col3:
                st.link_button("**自行获取 SA**", "https://chat.oaifree.com/token", use_container_width=True, type=button_type)
        st.write("")
    if set_choose == 'Fuclaude':
        with st.container(border=True):
            st.write("")
            st.write("##### Fuclaude 镜像服务")
            st.write("")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("**用户总数**", len(anthropic_data))
            with col2:
                st.metric("**Free总数**", len([i for i in anthropic_data.values() if i['type'] == 'Free']))
            with col3:
                st.metric("**PLUS总数**", len([i for i in anthropic_data.values() if i['type'] == 'Plus']))
            st.info("**此部分可查看使用 Fuclaude 服务的用户，仅支持更改SE_Token、删除 Fuclaude 服务下的用户**")
            st.write("")
            fields = ['账户', 'SE_Token', '用户组', '订阅类型']
            rows = [[user] + list(account.values()) for user, account in anthropic_data.items()]
            df = pd.DataFrame(rows, columns=fields)
            with st.expander("**表格工具**", expanded=False, icon=":material/construction:"):
                order = st.multiselect("**数据显示**", fields, web_setting["excel"]["order_fuclaude"], key="order_fuclaude")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    hide_index = st.selectbox("**隐藏索引**", [True, False], index=[True, False].index(web_setting["excel"]["hide_index_fuclaude"]), key="hide_index_fuclaude")
                with col2:
                    height = st.number_input("**表格高度**", value=web_setting["excel"]["height_fuclaude"], min_value=100, max_value=1000, step=100, key="height_fuclaude")
                with col3:
                    order_what = st.selectbox("**排序列名**", fields, index=fields.index(web_setting["excel"]["order_what_fuclaude"]), key="order_what_fuclaude")
                with col4:
                    order_row = st.selectbox("**排序方式**", ["默认", "升序", "降序"], index=["默认", "升序", "降序"].index( web_setting["excel"]["order_row_fuclaude"]), key="order_row_fuclaude")
                if order_row == "升序":
                    df = df.sort_values(by=order_what, ascending=True)
                elif order_row == "降序":
                    df = df.sort_values(by=order_what, ascending=False)

            edited_df_fuclaude = st.data_editor(df, column_order=order, hide_index=hide_index, use_container_width=True, height=height, disabled=['用户组', 'UID', '订阅类型'], num_rows="dynamic")
            col1, col2 = st.columns([0.2, 0.8])
            col3, col4 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存更改**", use_container_width=True, key="save_fuclaude", type=button_type):
                    json_data = df_to_json_fuclaude(edited_df_fuclaude)
                    for user in anthropic_data.keys():
                        if user not in edited_df_fuclaude['账户']:
                            user_data[user]["allow_claude"] = False
                            with open(current_path + 'users.json', 'w', encoding='utf-8') as json_file:
                                json_file.write(json.dumps(user_data, indent=2))
                    error = False
                    for user in edited_df_fuclaude['账户']:
                        if user not in user_data.keys():
                            error = True
                    if not error:
                        web_setting["excel"]["hide_index_fuclaude"] = hide_index
                        web_setting["excel"]["height_fuclaude"] = height
                        web_setting["excel"]["order_what_fuclaude"] = order_what
                        web_setting["excel"]["order_row_fuclaude"] = order_row
                        web_setting["excel"]["order_fuclaude"] = order
                        with open(current_path + '/setting.toml', 'w', encoding='utf-8') as f:
                            toml.dump(web_setting, f)
                        with open(current_path + '/anthropic.json', 'w', encoding='utf-8') as json_file:
                            json_file.write(json_data)
                        st.session_state.success = True
                        st.rerun()
                    else:
                        with col3:
                            st.error("**不允许在此表格内直接新增用户！请使用注册功能 新增用户 或 变更用户状态！**")
                            st.toast("**非法操作，请重试！**")
    if set_choose == '共享服务':
        with st.container(border=True):
            st.write('')
            st.write("##### Share 共享站")
            st.info("**建议开启 Share 功能时，将服务域名接入 道德审查 功能，以防止被恶意之人滥用！**", icon=':material/double_arrow:')
            share = st.checkbox("**开启Share账户共享功能**", value=web_setting["web"]["share"])
            if share:
                share_notice = st.text_area("**Share站公告** (支持MarkDown)", value=web_setting["web"]["share_notice"])
                share_list = share_data.keys()
                index = []
                for i in share_list:
                    index.append(list(openai_data.keys()).index(i))
                share_account = sac.transfer(items=openai_data.keys(), index=index, titles=['用户池', '共享池'],
                                             use_container_width=True, reload=True, align='center', search=True,
                                             pagination=True, width=500, height=400, color="dark")
            st.write("")
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存更改**", use_container_width=True, type=button_type, key="save_share_setting"):
                    logger.info(f"【管理员】 更改了共享服务设置！")
                    web_setting["web"]["share"] = share
                    if share:
                        web_setting["web"]["share_notice"] = share_notice
                        if share_account is None:
                            share_data = {}
                            with open(current_path + "share.json", "w") as share_file:
                                json.dump(share_data, share_file, indent=2)
                            st.toast("保存成功！", icon=":material/check_circle:")
                        else:

                            share_data = {
                                i: {
                                    "openai": {
                                        "token": openai_data[i]["token"] if user_data[i]["allow_chatgpt"] else None,
                                        "group": openai_data[i]["group"] if user_data[i]["allow_chatgpt"] else None,
                                        "type": openai_data[i]["type"] if user_data[i]["allow_chatgpt"] else None,
                                        "site_limit": openai_data[i]["site_limit"] if user_data[i]["allow_chatgpt"] else None,
                                        "expires_in": openai_data[i]["expires_in"] if user_data[i]["allow_chatgpt"] else None,
                                        "gpt35_limit": openai_data[i]["gpt35_limit"] if user_data[i]["allow_chatgpt"] else None,
                                        "gpt4_limit": openai_data[i]["gpt4_limit"] if user_data[i]["allow_chatgpt"] else None,
                                        "show_conversations": openai_data[i]["show_conversations"] if user_data[i]["allow_chatgpt"] else None
                                    },
                                    "anthropic": {
                                        "token": anthropic_data[i]["token"] if user_data[i]["allow_claude"] else None,
                                        "group": anthropic_data[i]["group"] if user_data[i]["allow_claude"] else None,
                                        "type": anthropic_data[i]["type"] if user_data[i]["allow_claude"] else None
                                    }
                                }
                                for i in share_account
                            }
                            with open(current_path + "share.json", "w") as share_file:
                                json.dump(share_data, share_file, indent=2)
                            st.toast("保存成功！", icon=":material/check_circle:")
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
            with col2:
                if st.button("**前往共享站**", use_container_width=True, type=button_type):
                    st.switch_page("pages/share.py")
    if set_choose == 'Oai-API':
        with st.container(border=True):
            st.write("##### Oai-API")
            st.info("**敬请期待...**", icon=':material/double_arrow:')
    if set_choose == '关于项目':
        with st.container(border=True):
            st.write("")
            st.write("##### 关于")
            st.write("")
            st.write(f"版本：OaiT {version}")
            st.write("作者：@Chenyme")
            st.write("鸣谢：@Neo")
            st.write("GitHub：https://github.com/Chenyme/oaifree-tools")
            st.write("有任何问题欢迎提 issue，如果觉得好用请给我一个 Star 吧，感谢支持！")
            st.info("""
                        本项目为开源项目，使用者必须在遵循 $OpenAI$ 和 $Claude$ 的 **使用条款** 以及 **法律法规** 的情况下使用，不得用于非法用途。

                        根据[**《生成式人工智能服务管理暂行办法》**](http://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)的要求，请勿对中国地区公众提供一切未经备案的生成式人工智能服务。""",
                    icon=':material/double_arrow:')
            st.write("")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**更多**", use_container_width=True, type=button_type):
                    readme()

            st.divider()
            st.write("##### 友情链接")
            st.write("")
            st.write("下面是 Neo博客站、Linux论坛、项目框架、个人其他项目的链接，欢迎访问！")
            st.write("")
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
                st.link_button("**视频翻译**", "https://github.com/Chenyme/Chenyme-AAVT", use_container_width=True, type=button_type)

else:
    if st.session_state.theme == "Simple White":
        with open(style_path + "//Simple_White.html", "r", encoding="utf-8") as file:
            classic_html = file.read()
            st.markdown(classic_html, unsafe_allow_html=True)

    elif st.session_state.theme == "Classic Black":
        with open(style_path + "//Classic_Black.html", "r", encoding="utf-8") as file:
            free_html = file.read()
            st.markdown(free_html, unsafe_allow_html=True)

    elif st.session_state.theme == "Retro Orange":
        with open(style_path + "//Retro_Orange.html", "r", encoding="utf-8") as file:
            Retro_Orange_html = file.read()
            Retro_Orange_html = Retro_Orange_html.replace("{{text}}", "Spark your creativity")
            st.markdown(Retro_Orange_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.28, 0.44, 0.28])
    with col2:
        if st.session_state.theme != "Retro Orange":
            sac.alert("**非法访问！**", "**警告：你无权进入该页面！**", color="error", size="lg", radius="lg", icon=True,
                      variant="filled", closable=True)
        st.write("")
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
            admin = st.text_input("**Admin Name：**", placeholder="Enter Admin Name / 管理账户")
            key = st.text_input("**Admin Key：**", type="password", placeholder="Enter Admin Key / 管理密钥")
            st.write("")
            if st.button("**Verify / 验证**", use_container_width=True, type=button_type):
                if admin == web_setting["web"]["super_user"] and key == web_setting["web"]["super_key"]:
                    st.session_state.role = "admin"
                    st.write("")
                    st.switch_page("pages/admin.py")
                else:
                    st.toast("**身份验证失败，如果您不是管理员请前往首页进行登录！**", icon=":material/error:")
            st.write("")
            if st.session_state.theme == "Retro Orange":
                st.page_link("home.py", label=":orange[HomePage / 首页]")
            else:
                st.page_link("home.py", label="**返回首页**")
            st.write("")

with open(style_path + "//footer.html", "r", encoding="utf-8") as file:
    footer_html = file.read()
    color = "white"
    if st.session_state.theme == "Retro Orange":
        color = "#efede4"
    footer_html = footer_html.replace("{{color}}", color)
st.markdown(footer_html, unsafe_allow_html=True)
st.logo("LOGO.png", link="https://github.com/Chenyme/oaifree-tools")
