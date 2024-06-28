import os
import re
import time
import json
import toml
import math
import logging
import zipfile
from io import BytesIO
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
from utils import get_accesstoken, get_sharetoken, df_to_json1, df_to_json2, df_to_json3



# 运行日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("app.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger()
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

# 读取配置文件
current_path = os.path.abspath('.') + '/config/'
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

    @st.experimental_dialog("邀请码设置")
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


    @st.experimental_dialog("站点迁移-配置导出")
    def download():
        st.write("")
        st.write("**请选择需要导出的配置文件**")
        st.write("")
        files = st.multiselect("选择的文件", ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json"], ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json"], label_visibility="collapsed")
        st.write("")
        if st.button("**导出数据**", use_container_width=True):
            st.write("")
            directory_path = current_path
            zip_buffer = BytesIO()
            try:
                sac.alert(label="准备数据中,请耐心等待...", color="info", variant='quote', size="md", radius="lg", icon=True, closable=True)
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for root, _, _ in os.walk(directory_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, directory_path)
                            zip_file.write(file_path, arcname)
                zip_buffer.seek(0)
                for file in files:
                    sac.alert(label=f"{file} 已准备完毕！", color="success", variant='quote', size="md", radius="lg", icon=True, closable=True)
                st.write("")
                st.download_button(
                    label="点击下载",
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
        st.write("")
        uploaded_file = st.file_uploader("上传配置文件", type=['zip'], label_visibility="collapsed")
        st.write("")
        st.write("")
        required_files = ["accounts.json", "config.json", "invite.json", "setting.toml", "share.json"]
        if st.button("**上传并配置**", use_container_width=True, type="primary"):
            if uploaded_file is not None:
                if uploaded_file.name.endswith('.zip'):
                    zip_buffer = BytesIO(uploaded_file.getvalue())
                    with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                        zip_file_list = zip_ref.namelist()
                        success_files = [file for file in required_files if file in zip_file_list]
                        error_files = [file for file in zip_file_list if file not in required_files]
                        sac.alert(label="上传成功！请稍等片刻，正在配置文件...", color="info", variant='quote', size="md", radius="lg", icon=True, closable=True)
                        for file in success_files:
                            zip_ref.extract(file, current_path)
                            sac.alert(label=f"{file} 配置成功！", color="success", variant='quote', size="md", radius="lg", icon=True, closable=True)
                        for file in error_files:
                            sac.alert(label=f"未知文件 {file}", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
                    sac.alert(label="所有文件均成功配置！请及时刷新界面以生效！", banner=True, color="success", variant='filled', size="md", radius="lg", icon=True, closable=True)
                else:
                    st.error("上传失败，请上传正确的配置文件！", icon=":material/error:")
            else:
                sac.alert(label="请先上传文件！", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)

        st.write("")

    st.write("## 欢迎！" + web_setting["web"]["super_user"])

    set_choose = sac.segmented(
        items=[
            sac.SegmentedItem(label='运行日志', icon='file-text'),
            sac.SegmentedItem(label='基本设置', icon='gear-fill'),
            sac.SegmentedItem(label='号池管理', icon='pc-display'),
            sac.SegmentedItem(label='用户管理', icon='person-fill-gear'),
            sac.SegmentedItem(label='更多功能', icon='github'),
        ], align='center', use_container_width=True, color='dark'
    )

    if set_choose == '运行日志':
        if web_setting["web"]["super_key"] == "12345678":
            key()
        with st.container(border=True):
            st.write("")
            st.write("**站点信息**")

            user_names = config.keys()
            size_bytes1 = os.path.getsize("app.log")
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
            col3.metric("服务次数", st.session_state.count_people, st.session_state.count_people)
            col4.metric("日志信息", size1, size_bytes1-35)
            col5.metric("配置信息", size2, size_bytes2-2463)

            with col1:
                if st.button("**导出配置**", use_container_width=True):
                    download()
            with col2:
                if st.button("**导入配置**", use_container_width=True):
                    upload()

            st.divider()
            with open('app.log', 'r', encoding='utf-8') as file:
                lines = file.readlines()
            with open('app.log', 'r', encoding='utf-8') as file:
                logs = file.read()
            pattern = re.compile(
                r'(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2},\d{3} - INFO - 【(用户登录|管理登录)】 (?:用户：|管理员：)(\w+) 登录成功！'
            )
            matches = pattern.findall(logs)
            st.write('**服务总览**')
            if matches:
                st.session_state.count_people = len(matches)
                data = pd.DataFrame(matches, columns=['日期', 'login_type', 'user'])
                summary = data.groupby(['日期', 'user']).size().reset_index(name='登录总计')
                pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
                st.write("")
                st.bar_chart(pivot_table)
            else:
                sac.alert(label="暂无服务记录，快去使用吧！", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)

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
                    with open("app.log", "w", encoding="utf-8") as log_file:
                        log_file.write(log_content)
                    st.rerun()
                st.write("")

    if set_choose == '基本设置':
        with st.container(border=True):
            st.write("")
            st.write("**网站设置**")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("**站点标题**", value=web_setting["web"]["title"])
                subtitle = st.text_input("**站点副标题**", value=web_setting["web"]["subtitle"])
                notice_enable = st.selectbox("**开启站点公告 (支持markdown)**", [True, False], index=[True, False].index(web_setting["web"]["notice_enable"]))
            with col2:
                domain = st.text_input("**服务域名**", value=web_setting["web"]["domain"])
                super_user = st.text_input("**管理员昵称**", value=web_setting["web"]["super_user"])
                super_key = st.text_input("**管理员密钥**", value=web_setting["web"]["super_key"])

            st.write("")
            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                if st.button(" **保存设置**", use_container_width=True):
                    web_setting["web"]["title"] = title
                    web_setting["web"]["subtitle"] = subtitle
                    web_setting["web"]["notice_enable"] = notice_enable
                    web_setting["web"]["domain"] = domain
                    web_setting["web"]["super_user"] = super_user
                    web_setting["web"]["super_key"] = super_key
                    with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                        toml.dump(web_setting, f)
                    logger.info(f"<管理员> 【基本设置】 更新了网站基本设置！")
                    st.toast("保存成功!", icon=':material/check_circle:')
                    st.toast("即将刷新页面!", icon=':material/check_circle:')
                    time.sleep(1)
                    st.rerun()

            st.divider()
            st.write("**公告设置**")
            col1, col2 = st.columns(2)
            with col1:
                notice_title = st.text_area("**站点公告-主标题**", value=web_setting["web"]["notice_title"], height=100)
                notice_subtitle = st.text_area("**站点公告-次标题**", value=web_setting["web"]["notice_subtitle"], height=100)
                notice_banner = st.checkbox("**启用公告滚动效果**", value=web_setting["web"]["notice_banner"])
            with col2:
                style = ['light', 'filled', 'outline', 'transparent', 'quote', 'quote-light']
                color = ['success', 'info', 'warning', 'error', 'dark', 'gray', 'red', 'pink', 'grape', 'violet', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange']
                size = ['xs', 'sm', 'md', 'lg', 'xl']
                col3, col4 = st.columns([0.5, 0.5])
                with col3:
                    notice_size = st.selectbox("**公告大小**", size, index=size.index(web_setting["web"]["notice_size"]))
                    notice_radius = st.selectbox("**公告圆角**", size, index=size.index(web_setting["web"]["notice_radius"]))
                with col4:
                    notice_style = st.selectbox("**公告样式**", style, index=style.index(web_setting["web"]["notice_style"]))
                    notice_color = st.selectbox("**公告颜色**", color, index=color.index(web_setting["web"]["notice_color"]))
                st.write("**样式预览**")
            with col2:
                sac.alert(label=notice_title, description=notice_subtitle,
                          color=notice_color, banner=notice_banner,
                          variant=notice_style, size=notice_size, radius=notice_radius, icon=True, closable=True)

            st.write("")
            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                if st.button("**保存公告**", use_container_width=True):
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
            st.write("**账户列表**")
            sac.alert(label="**各模块用户组相互对应，请谨慎修改！** 若直接在表格上修改，请及时**点击保存按钮**！", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            df1 = pd.DataFrame(rows, columns=['用户组', '订阅类型', '账户邮箱', 'AC_Token', 'RF_Token'])
            edited_df1 = st.data_editor(df1, hide_index=True, use_container_width=True, num_rows="dynamic", height=248)

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
            st.write("**注册设置**")
            sac.alert(label="您**必须重新设置至少一个注册码**，并及时**保存更改**，同一个组别允许对应多个邀请码", variant='quote', color="warning", size="md", radius="lg", icon=True, closable=True)
            rows = [[IV_Token, invite_config[IV_Token]] for IV_Token, Group in invite_config.items()]
            df3 = pd.DataFrame(rows, columns=['invite_token', 'group'])
            edited_df3 = st.data_editor(df3, hide_index=True, use_container_width=True, height=248, num_rows="dynamic", column_config={"group": st.column_config.SelectboxColumn(options=accounts.keys())})

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
                        with open(current_path + json_filename, 'w', encoding='utf-8') as json_file:
                            json_file.write(json_data3)
                        st.toast("保存成功!", icon=':material/check_circle:')
                        logger.info(f"<管理员> 【邀请码更改】 更新了邀请码信息！")
                    else:
                        with col6:
                            sac.alert(label="保存失败！您必须设置完整的注册码并选择正确的组别，不允许为空值!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
            with col2:
                if st.button("**邀请码设置**", use_container_width=True):
                    invite()

            st.divider()
            st.write("**AC_Token刷新策略**")
            refresh = st.checkbox("**启用用户登陆时自动刷新AC**", value=web_setting["web"]["refresh_all"])
            user_refresh = st.checkbox("**允许过期时用户可自行刷新AC**", value=web_setting["web"]["user_refresh"])

            st.write("")
            st.write("**AC_Token刷新**")
            ac_group = st.selectbox("**刷新的组别**", accounts.keys(), label_visibility="collapsed")
            col1, col2, col3, col4, col5 = st.columns(5)
            col6, col7 = st.columns([0.99999, 0.00001])
            with col1:
                if st.button(f"**刷新 - {ac_group}**", use_container_width=True):
                    user_re_tk = accounts[ac_group]["refresh_token"]
                    if user_re_tk is None or user_re_tk == "":
                        st.write("")
                        with col6:
                            sac.alert(label="刷新失败，请填写正确的refresh-token!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
                        logger.info(f"<管理员> 【AC刷新】 刷新 {ac_group} 组的AC_Token时失败！")
                    else:
                        user_ac_tk = get_accesstoken(user_re_tk)
                        if user_ac_tk is None or user_ac_tk == "":
                            st.write("")
                            with col6:
                                sac.alert(label="刷新失败，请检查refresh-token是否有效!", color="error", variant='quote', size="md", radius="lg", icon=True, closable=True)
                            logger.info(f"<管理员> 【AC刷新】 刷新 {ac_group} 组的AC_Token时失败！")
                        else:
                            accounts[ac_group]["access_token"] = user_ac_tk
                            accounts_json = json.dumps(accounts, indent=2)
                            json_filename = 'accounts.json'
                            with open(current_path + json_filename, 'w', encoding='utf-8') as json_file:
                                json_file.write(accounts_json)
                            logger.info(f"<管理员> 【AC刷新】 成功刷新 {ac_group} 组的AC_Token！")
                            st.toast("刷新成功！", icon=':material/check_circle:')
                            st.toast("即将刷新页面...1s", icon=':material/check_circle:')
                            time.sleep(1)

            web_setting["web"]["refresh_all"] = refresh
            web_setting["web"]["user_refresh"] = user_refresh
            with open(current_path + "setting.toml", "w", encoding="utf-8") as f:
                toml.dump(web_setting, f)

            st.write("")

    if set_choose == '用户管理':
        with st.container(border=True):
            st.write('')
            st.write("**用户列表**")
            sac.alert(label="`site_limit` 表示限制的网站名称，为空则无限制；`expires_in` 表示过期的秒数，为 0 则永不过期；`gpt35_limit` 表示gpt-3.5可使用的次数，为 -1 则无限制；`gpt4_limit` 表示gpt-4可使用的次数，为 -1 则无限制；`show_conversations` 表示是否会话无需隔离，为 false 则隔离。", color="warning", variant='quote', size="md", radius="lg", icon=True, closable=True)
            try:
                fields = ['username'] + list(next(iter(config.values())).keys())
                rows = [[user] + list(account.values()) for user, account in config.items()]
                df2 = pd.DataFrame(rows, columns=fields)
                edited_df2 = st.data_editor(df2, hide_index=True, use_container_width=True, height=248, disabled=["group", "type", "site_limit", "expires_in", "gpt35_limit", "gpt4_limit", "show_conversations"], num_rows="dynamic")
            except:
                sac.alert(label="无数据！用户列表为空！请在下方的注册模块注册新用户！", color="error", variant='quote',size="md", radius="lg", icon=True, closable=True)
            st.write('')
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("**保存修改** ", use_container_width=True):
                    json_data2 = df_to_json2(edited_df2)
                    json_filename = 'config.json'
                    with open(current_path + json_filename, 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data2)
                    st.toast("保存修改成功！", icon=':material/check_circle:')
                    logger.info(f"<管理员> 【用户更改】 更新了用户信息！")
            with col2:
                st.link_button("**获取SA_Token**", "https://chat.oaifree.com/token", use_container_width=True)

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

            st.divider()
            st.write("**关于**")
            st.write("版本：OaiT V1.1.0")
            st.write("作者：@Chenyme")
            st.write("GitHub：https://github.com/Chenyme/oaifree-tools")
            st.write("有任何问题欢迎提issue，如果觉得好用请给我一个Star吧，感谢支持！")

            st.divider()
            st.write("**友情链接**")
            sac.buttons([sac.ButtonsItem("GitHub", href="https://github.com/Chenyme", color="dark"), sac.ButtonsItem("Linux.do", href="https://linux.do", color="dark"), sac.ButtonsItem("zhile.io", href="https://zhile.io/", color="dark"), sac.ButtonsItem("Streamlit", href="https://streamlit.io", color="dark"), sac.ButtonsItem("我的其他项目", href="https://github.com/Chenyme/Chenyme-AAVT", color="dark")], use_container_width=True, color="dark", index=None, variant="filled")


    col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
    with col2:
        st.image("LOGO.png", width=200, caption="一键管理Oaifree镜像服务，简单上手", use_column_width=True)


else:
    col1, col2, col3 = st.columns(3)
    with col2:
        sac.alert("**非法访问！**", "**警告：你无权进入该页面！**", color="error", size="lg", radius="lg", icon=True, closable=True)
        with st.container(border=True):
            st.write("")
            col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
            with col2:
                st.image("LOGO.png", width=200, use_column_width=True)
            st.write("")
            st.write("")
            admin = st.text_input("**管理员：**")
            st.write("")
            key = st.text_input("**密钥：**")
            st.write("")
            st.write("")
            st.write("")
            if st.button("验证", use_container_width=True):
                if admin == web_setting["web"]["super_user"] and key == web_setting["web"]["super_key"]:
                    st.session_state.role = "admin"
                    logger.info(f"【管理登录】 管理员：{admin} 登录成功！")
                    st.write("")
                    st.page_link("pages/admin.py", label="进入管理面板", icon=":material/admin_panel_settings:",
                                 use_container_width=True)
            st.write("")
            st.write("")
