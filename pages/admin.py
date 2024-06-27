import os
import re
import time
import json
import toml
import math
import logging
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
from utils import get_accesstoken, get_sharetoken, df_to_json1, df_to_json2, df_to_json3

if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role == "admin":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("app.log", encoding='utf-8'),
                                  logging.StreamHandler()])

    logger = logging.getLogger()

    png_logger = logging.getLogger("PIL.PngImagePlugin")
    png_logger.setLevel(logging.WARNING)
    urllib3_logger = logging.getLogger("urllib3.connectionpool")
    urllib3_logger.setLevel(logging.WARNING)

    current_path = os.path.abspath('.')
    with open(current_path + '/invite.json', 'r', encoding='utf-8') as file:
        invite_config = json.load(file)
    with open(current_path + '/config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    with open(current_path + '/accounts.json', 'r', encoding='utf-8') as file:
        accounts = json.load(file)
    with open(current_path + '/setting.toml', 'r', encoding='utf-8') as file:
        web_setting = toml.load(file)

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
        """, unsafe_allow_html=True)

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
        """, unsafe_allow_html=True)


    @st.experimental_dialog("安全保护")
    def key():
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
                with open("setting.toml", "w", encoding="utf-8") as f:
                    toml.dump(web_setting, f)

                logger.info(f"【密钥修改】 管理员修改了新的密钥！")
                st.rerun()


    @st.experimental_dialog("默认设置")
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
            with open("setting.toml", "w", encoding="utf-8") as f:
                toml.dump(web_setting, f)
            logger.info(f"【邀请码设置】 管理员更新了邀请码默认设置！")
            sac.alert(label="保存成功！", color="success", variant='quote', size="md", radius="lg", icon=True, closable=True)
        st.write("")

    st.write("## 欢迎！" + web_setting["web"]["super_user"])

    set_choose = sac.segmented(
        items=[
            sac.SegmentedItem(label='运行日志', icon='file-text'),
            sac.SegmentedItem(label='基本设置', icon='gear-fill'),
            sac.SegmentedItem(label='号池管理', icon='pc-display'),
            sac.SegmentedItem(label='用户管理', icon='person-fill-gear'),
            sac.SegmentedItem(label='GitHub', icon='github', href='https://github.com/Chenyme/oaifree-tools'),
        ], align='center', use_container_width=True, color='dark'
    )

    if set_choose == '基本设置':
        with st.container(border=True):
            st.write("")
            st.write("**网站设置**")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("**站点标题**", value=web_setting["web"]["title"])
                subtitle = st.text_input("**站点副标题**", value=web_setting["web"]["subtitle"])
                notice_enable = st.selectbox("**站点公告(支持markdown)**", [True, False], index=[True, False].index(web_setting["web"]["notice_enable"]))
            with col2:
                domain = st.text_input("**服务域名**", value=web_setting["web"]["domain"])
                super_user = st.text_input("**管理员昵称**", value=web_setting["web"]["super_user"])
                super_key = st.text_input("**管理员密钥**", value=web_setting["web"]["super_key"])

            st.write("")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存网站设置**", use_container_width=True):
                    web_setting["web"]["title"] = title
                    web_setting["web"]["subtitle"] = subtitle
                    web_setting["web"]["notice_enable"] = notice_enable
                    web_setting["web"]["domain"] = domain
                    web_setting["web"]["super_user"] = super_user
                    web_setting["web"]["super_key"] = super_key
                    with open("setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    logger.info(f"【基本设置】 管理员更新了基本设置！")
                    st.toast("保存成功!", icon=':material/check_circle:')
                    msg = st.toast("即将刷新页面...2s", icon=':material/check_circle:')
                    time.sleep(1)
                    msg.toast("即将刷新页面...1s", icon=':material/check_circle:')
                    time.sleep(1)

            st.divider()
            st.write("**站点公告**")
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                notice_title = st.text_area("**站点公告-主标题**", value=web_setting["web"]["notice_title"], height=100)
                notice_subtitle = st.text_area("**站点公告-次标题**", value=web_setting["web"]["notice_subtitle"], height=130)

            with col2:
                notice_banner = st.checkbox("**启用公告滚动效果**", value=web_setting["web"]["notice_banner"])

                style = ['light', 'filled', 'outline', 'transparent', 'quote', 'quote-light']
                color = ['success', 'info', 'warning', 'error', 'dark']
                col3, col4 = st.columns([0.5, 0.5])
                with col3:
                    notice_style = st.selectbox("**公告样式**", style, index=style.index(web_setting["web"]["notice_style"]))
                with col4:
                    notice_color = st.selectbox("**公告颜色**", color, index=color.index(web_setting["web"]["notice_color"]))
                st.write("**Preview**")
                sac.alert(label=notice_title, description=notice_subtitle,
                          color=notice_color, banner=notice_banner,
                          variant=notice_style, size="md", radius="md", icon=True, closable=True)

            st.write("")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存公告设置**", use_container_width=True):
                    web_setting["web"]["notice_enable"] = notice_enable
                    web_setting["web"]["notice_banner"] = notice_banner
                    web_setting["web"]["notice_style"] = notice_style
                    web_setting["web"]["notice_title"] = notice_title
                    web_setting["web"]["notice_color"] = notice_color
                    web_setting["web"]["notice_subtitle"] = notice_subtitle
                    with open("setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    logger.info(f"【公告设置】 管理员更新了网站公告！")

            st.divider()
            st.write("**注册设置**")
            sac.alert(label="您**必须重新设置至少一个注册码**，并**保存更改**，同一个组别允许使用多个邀请码", variant='quote', color="warning", size="md", radius="lg", icon=True, closable=True)
            rows = [[invi, invite_config[invi]]
                    for invi, gro in invite_config.items()]
            df3 = pd.DataFrame(rows, columns=['invite_token', 'group'])
            edited_df3 = st.data_editor(df3, hide_index=True, use_container_width=True, num_rows="dynamic",
                                        column_config={"group": st.column_config.SelectboxColumn(
                                            options=accounts.keys())})

            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button("**保存邀请码**", use_container_width=True):
                    dict_for_check, json_data3 = df_to_json3(edited_df3)
                    json_filename = 'invite.json'
                    success = 0
                    for a, b in dict_for_check.items():
                        if a is not None and b is not None and a != 'None' and b != 'None' and a != '' and b != '':
                            success = 1
                        else:
                            success = 0
                    if json_data3 != "{}" and success:
                        with open(json_filename, 'w', encoding='utf-8') as json_file:
                            json_file.write(json_data3)
                        st.toast("保存成功!", icon=':material/check_circle:')
                        logger.info(f"【邀请码更改】 管理员更新了邀请码信息！")
                    else:
                        with col6:
                            sac.alert(label="保存失败！您必须设置完整的注册码并选择正确的组别，不允许为空值!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
            with col2:
                if st.button("**邀请码设置**", use_container_width=True):
                    invite()

            st.write("")

    if set_choose == '号池管理':
        with st.container(border=True):
            st.write('')
            rows = [[groups, datas['Account'], datas['access_token'], datas['refresh_token']]
                    for groups, datas in accounts.items()]
            st.write("**账户列表**")
            sac.alert(label="Group一旦输入确定，请勿随意修改!", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            df1 = pd.DataFrame(rows, columns=['groups', 'Account', 'access_token', 'refresh_token'])
            edited_df1 = st.data_editor(df1, hide_index=True, use_container_width=True, num_rows="dynamic")

            st.write('')
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存账户信息**", use_container_width=True):
                    json_data1 = df_to_json1(edited_df1)
                    json_filename = 'accounts.json'
                    with open(json_filename, 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data1)
                    logger.info(f"【账户更改】 管理员更新了账户信息！")
                    st.toast("保存成功!", icon=':material/check_circle:')
            with col2:
                st.link_button("**获取Refresh_token**", "https://token.oaifree.com/auth", use_container_width=True)

            st.divider()
            st.write("**刷新Access_token**")
            ac_group = st.selectbox("**Access_token**", accounts.keys(), label_visibility="collapsed")
            st.write("")
            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button(f"**刷新组别 - {ac_group}**", use_container_width=True):
                    user_re_tk = accounts[ac_group]["refresh_token"]
                    if user_re_tk is None or user_re_tk == "":
                        st.write("")
                        with col6:
                            sac.alert(label="刷新失败，请填写正确的refresh-token!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
                        logger.info(f"【AC刷新】 管理员刷新{ac_group}的Access_token失败！")
                    else:
                        user_ac_tk = get_accesstoken(user_re_tk)
                        if user_ac_tk is None or user_ac_tk == "":
                            st.write("")
                            with col6:
                                sac.alert(label="刷新失败，请检查refresh-token是否有效!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
                            logger.info(f"【AC刷新】 管理员刷新{ac_group}的Access_token失败！")
                        else:
                            accounts[ac_group]["access_token"] = user_ac_tk
                            accounts_json = json.dumps(accounts, indent=2)
                            json_filename = 'accounts.json'
                            with open(json_filename, 'w', encoding='utf-8') as json_file:
                                json_file.write(accounts_json)
                            logger.info(f"【AC刷新】 管理员刷新{ac_group}的Access_token成功！")
                            st.toast("刷新成功！", icon=':material/check_circle:')
                            msg = st.toast("即将刷新页面...3s", icon=':material/check_circle:')
                            time.sleep(1)
                            msg.toast("即将刷新页面...2s", icon=':material/check_circle:')
                            time.sleep(1)
                            msg.toast("即将刷新页面...1s", icon=':material/check_circle:')
                            time.sleep(1)

            st.divider()
            st.write("**刷新策略**")
            refresh = st.checkbox("用户登陆时自动刷新AC", value=web_setting["web"]["refresh_all"])
            user_refresh = st.checkbox("过期时用户自行刷新AC", value=web_setting["web"]["user_refresh"])
            web_setting["web"]["refresh_all"] = refresh
            web_setting["web"]["user_refresh"] = user_refresh
            with open("setting.toml", "w", encoding="utf-8") as f:
                toml.dump(web_setting, f)

            st.write("")

    if set_choose == '用户管理':
        with st.container(border=True):
            st.write('')
            st.write("**用户列表**")
            sac.alert(label="`site_limit` 表示限制的网站名称，为空则无限制；`expires_in` 表示过期的秒数，为 0 则永不过期；`gpt35_limit` 表示gpt-3.5可使用的次数，为 -1 则无限制；`gpt4_limit` 表示gpt-4可使用的次数，为 -1 则无限制；`show_conversations` 表示是否会话无需隔离，为 false 则隔离。", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            fields = ['username'] + list(next(iter(config.values())).keys())
            rows = [[user] + list(account.values()) for user, account in config.items()]
            df2 = pd.DataFrame(rows, columns=fields)
            edited_df2 = st.data_editor(df2, hide_index=True, use_container_width=True,
                                        disabled=["group", "site_limit", "expires_in", "gpt35_limit", "gpt4_limit", "show_conversations"], num_rows="dynamic")
            st.write('')
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存用户修改**", use_container_width=True):
                    json_data2 = df_to_json2(edited_df2)
                    json_filename = 'config.json'
                    with open(json_filename, 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data2)
                    st.toast("保存修改成功！", icon=':material/check_circle:')
                    logger.info(f"【用户更改】 管理员更新了用户信息！")
            with col2:
                st.link_button("**手动获取Share_token**", "https://chat.oaifree.com/token", use_container_width=True)

            st.divider()
            st.write("**新用户注册**")
            col1, col2 = st.columns(2)
            with col1:
                user_new_acc = st.text_input("**账户**")
                user_new_pass = st.text_input("密码")
                user_new_group = st.selectbox("组别", accounts.keys())
                show_conversations = st.selectbox("会话无需隔离", ['true', 'false'], index=1, help="false为隔离会话")
            with col2:
                site_limit = st.text_input("限制网站（为空不限制）", value="", help="限制的网站, 为空则不限制")
                expires_in = st.number_input("有效期（秒）", value=0, help="token有效期（单位为秒），填 0 则永久有效")
                gpt35_limit = st.number_input("限制GPT-3.5", value=-1, help="GPT-3.5对话限制，填 -1 则不限制")
                gpt4_limit = st.number_input("限制GPT-4", value=-1, help="GPT-4对话限制，填 -1 则不限制")
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
                        new_name, new_token_key = get_sharetoken(user_new_acc, acc, site_limit, expires_in, gpt35_limit, gpt4_limit, show_conversations)

                        json_data = {
                            new_name: {
                                'password': user_new_pass,
                                'token': new_token_key,
                                'group': user_new_group,
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
                        with open(json_filename, 'w', encoding='utf-8') as json_file:
                            json_file.write(config_json)
                        st.toast("注册成功！", icon=':material/check_circle:')
                        msg = st.toast("即将刷新页面...3s", icon=':material/check_circle:')
                        time.sleep(1)
                        msg.toast("即将刷新页面...2s", icon=':material/check_circle:')
                        time.sleep(1)
                        msg.toast("即将刷新页面...1s", icon=':material/check_circle:')
                        time.sleep(1)
                        logger.info(f"【用户注册】 管理员注册了新用户 {new_name}，token:{new_token_key}，group:{user_new_group}！")
                        st.rerun()
                st.write("")
            with col2:
                if st.button("**前往首页登录**", use_container_width=True):
                    st.switch_page("home.py")

    if set_choose == '运行日志':
        if web_setting["web"]["super_key"] == "12345678":
            key()
        with st.container(border=True):
            user_names = config.keys()
            size_bytes = os.path.getsize("app.log")
            if size_bytes == 0:
                size = "0B"
            else:
                size_name = ("B", "KB", "MB", "GB", "TB")
                i = int(math.floor(math.log(size_bytes, 1024)))
                p = math.pow(1024, i)
                s = round(size_bytes / p, 2)
                size = f"{s} {size_name[i]}"

            st.write("")
            st.write("**基本信息**")
            col1, col2, col3 = st.columns(3)
            col1.metric("用户总数", len(user_names), len(user_names)-3)
            col2.metric("号池总数", len(accounts.keys()), len(accounts.keys())-1)
            col3.metric("缓存占用", size, size_bytes-35)

            st.divider()
            with open('app.log', 'r', encoding='utf-8') as file:
                lines = file.readlines()
            with open('app.log', 'r', encoding='utf-8') as file:
                logs = file.read()
            pattern = re.compile(
                r'(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2},\d{3} - root - INFO - 【(用户登录|管理登录)】 (?:用户：|管理员：)(\w+) 登录成功！'
            )

            matches = pattern.findall(logs)
            st.write('**登录总览**')
            if matches:
                data = pd.DataFrame(matches, columns=['日期', 'login_type', 'user'])
                summary = data.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                st.write("")
                st.bar_chart(pivot_table)
            else:
                sac.alert(label="暂无登录记录，快去使用吧", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)

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
                    log_content = "\n【OaiT服务已成功开启！】"
                    with open("app.log", "w", encoding="utf-8") as log_file:
                        log_file.write(log_content)
                    st.rerun()
                st.write("")

    col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
    with col2:
        st.image("LOGO.png", width=200, caption="一键管理Oaifree服务，简单上手", use_column_width=True)
else:
    sac.alert("非法访问！", "你无权进入该页面！", color="error", size="md", radius="lg", icon=True, closable=True)