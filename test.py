import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os

current_path = os.path.dirname(os.path.abspath(__file__)) + '/config/'
with open(current_path + 'app.log', 'r', encoding='utf-8') as file:
    logs = file.read()

# 提取匹配的日志记录
pattern_user = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【用户登录】 用户：(\w+) 登录成功！')
pattern_share = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【Share登录】 共享账户：(\w+) 被登录！')
pattern_sign = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}):\d{2}:\d{2},\d{3} - INFO - 【用户注册】 新用户：(\w+) 注册成功！')

matches_user = pattern_user.findall(logs)
matches_share = pattern_share.findall(logs)
matches_sign = pattern_sign.findall(logs)

# 合并所有日期
all_dates = [datetime.strptime(date, '%Y-%m-%d %H').date() for date, _ in matches_user + matches_share + matches_sign]
min_date = min(all_dates) if all_dates else datetime.today().date()
max_date = max(all_dates) if all_dates else datetime.today().date()

# 创建 Streamlit 交互元素
plot_choose = st.radio('选择图表类型', ['登录统计柱状图', '登录统计折线图', '用户服务统计图', '共享服务统计图', '注册人数统计图', '时段人数统计图'])
start_date = st.date_input("选择开始日期", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.date_input("选择结束日期", value=max_date, min_value=min_date, max_value=max_date)

height = st.slider('图表高度', 200, 800, 400)
horizontal = st.checkbox('水平显示')

data_user = pd.DataFrame(matches_user, columns=['日期时间', 'user'])
data_share = pd.DataFrame(matches_share, columns=['日期时间', 'user'])
data_sign = pd.DataFrame(matches_sign, columns=['日期时间', 'user'])

data_user['日期'] = pd.to_datetime(data_user['日期时间']).dt.date
data_share['日期'] = pd.to_datetime(data_share['日期时间']).dt.date
data_sign['日期'] = pd.to_datetime(data_sign['日期时间']).dt.date

filtered_user = data_user[(data_user['日期'] >= start_date) & (data_user['日期'] <= end_date)]
filtered_share = data_share[(data_share['日期'] >= start_date) & (data_share['日期'] <= end_date)]
filtered_sign = data_sign[(data_sign['日期'] >= start_date) & (data_sign['日期'] <= end_date)]

# 按天显示登录统计柱状图
if plot_choose == '登录统计柱状图':
    if not filtered_user.empty or not filtered_share.empty:
        matches = pd.concat([filtered_user, filtered_share])
        st.session_state.count_people = len(matches)
        matches['日期'] = matches['日期'].astype(str)
        summary = matches.groupby(['日期', 'user']).size().reset_index(name='登录总计')
        pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
        st.write("")
        st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)
    else:
        sac.a

# 按天显示登录统计折线图
if plot_choose == '登录统计折线图':
    if not filtered_user.empty or not filtered_share.empty:
        matches = pd.concat([filtered_user, filtered_share])
        matches['日期'] = matches['日期'].astype(str)
        user_login_counts = matches.groupby(['日期', 'user']).size().unstack(fill_value=0).reset_index()
        user_login_counts['总登录数'] = user_login_counts.select_dtypes(include=['number']).sum(axis=1)
        st.line_chart(data=user_login_counts.set_index('日期'), use_container_width=True, height=height)

# 按天显示用户服务统计图
if plot_choose == '用户服务统计图':
    if not filtered_user.empty:
        filtered_user['日期'] = filtered_user['日期'].astype(str)
        summary = filtered_user.groupby(['日期', 'user']).size().reset_index(name='登录总计')
        pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
        st.write("")
        st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)

# 按天显示共享服务统计图
if plot_choose == '共享服务统计图':
    if not filtered_share.empty:
        filtered_share['日期'] = filtered_share['日期'].astype(str)
        summary = filtered_share.groupby(['日期', 'user']).size().reset_index(name='登录总计')
        pivot_table = summary.pivot(index='日期', columns='user', values='登录总计').fillna(0)
        st.write("")
        st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)

# 按天显示注册人数统计图
if plot_choose == '注册人数统计图':
    if not filtered_sign.empty:
        filtered_sign['日期'] = filtered_sign['日期'].astype(str)
        summary = filtered_sign.groupby(['日期', 'user']).size().reset_index(name='注册总计')
        pivot_table = summary.pivot(index='日期', columns='user', values='注册总计').fillna(0)
        st.write("")
        st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)

# 显示时段人数统计图
if plot_choose == '时段人数统计图':
    if not filtered_user.empty:
        data = filtered_user.copy()
        data['时段'] = pd.to_datetime(data['日期时间']).dt.hour
        data['时段'] = data['时段'].apply(lambda hour: (
            '00:00-04:00' if 0 <= hour < 4 else
            '04:00-08:00' if 4 <= hour < 8 else
            '08:00-12:00' if 8 <= hour < 12 else
            '12:00-16:00' if 12 <= hour < 16 else
            '16:00-20:00' if 16 <= hour < 20 else
            '20:00-24:00'
        ))

        summary = data.groupby(['日期', '时段']).size().reset_index(name='登录总计')
        summary['日期时段'] = summary['日期'].astype(str) + ' ' + summary['时段']
        pivot_table = summary.pivot(index='日期时段', columns='时段', values='登录总计').fillna(0)

        st.write("")
        st.bar_chart(pivot_table, height=height, use_container_width=True, horizontal=horizontal)