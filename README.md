<div align="center">
  
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/LOGO.png" alt="Logo" width="100">

![GitHub License](https://img.shields.io/github/license/chenyme/oaifree-tools)
![Docker Image Size](https://img.shields.io/docker/image-size/chenyme/oait)
![Docker Image Version](https://img.shields.io/docker/v/chenyme/oait)
![GitHub Repo stars](https://img.shields.io/github/stars/chenyme/oaifree-tools)


</div>

## 项目功能
  - **UID**：UID标识/UID登录/UID改密
  - **个性化**：站点标题/站点公告/登录主题/按钮样式
  - **站点工具**：登录统计/运行日志/站点迁移/数据导出
  - **用户权限**：自助登录/自助续费/自由改密/自由共享
  - **账户管理**：账号/用户/共享池管理、账户/共享/新用户权限
  - **域名管理**：负载分流/新旧 UI/延迟测速/自定义域名/自由选择
  - **授权令牌**：邀请令牌(注册)/刷新令牌(续费)/链接发卡网站/自助发卡
  - **Token 管理**：SAToken/ACToken自动/手动检测、自动刷新SAToken/ACToken

## 项目部署
#### docker
```shell
docker pull chenyme/oait:v1.1.5
docker run -d -p 8501:8501 chenyme/oait:v1.1.5

# docker pull ghcr.io/chenyme/oait:latest
# docker run -d -p 8501:8501 ghcr.io/chenyme/oait:latest
```

#### Git
```shell
git clone https://github.com/Chenyme/oaifree-tools
docker build -t chenyme/oait:v1.1.5 .
docker run -d -p 8501:8501 chenyme/oait:v1.1.5
```

#### Python
```shell
git clone https://github.com/Chenyme/oaifree-tools
cd oaifree-tools
streamlit run home.py
```

## 更新/迁移
在`项目运行`日志下导出所有配置文件

```shell
docker pull chenyme/oait:v1.1.5
docker run -d -p 8501:8501 chenyme/oait:v1.1.5

# docker pull ghcr.io/chenyme/oait:latest
# docker run -d -p 8501:8501 ghcr.io/chenyme/oait:latest
```

登录管理后台，在`项目运行`日志下导入所有配置文件

## 首次使用

首次登录请**及时修改账户密码**，以及对应的**邀请码**

默认管理账号：`admin`

管理密码：`12345678`

默认的邀请码有三个，请及时修改（可删除其中两个，再修改一个）

<table>
  <tr>
    <td><img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/login-admin.png" /></td>
    <td><img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/admin-keychange.png" /></td>
  </tr>
</table>


## 主要功能

#### 用户登录

管理员页面独立验证

支持Oauth登录，防止Token泄露

<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/login.png" />

#### 运行日志

查看站点情况

支持检查用户登录情况、服务运行日志

<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/admin-preview.png" />

#### 基本设置

支持更改站点标题、说明

支持发布站点公告、修改公告样式

支持用户注册，邀请码注册，管理注册者使用权限

<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/admin-basicsetting.png" />

#### 号池管理

支持多个AccessToken使用、管理

支持手动/自动刷新AccessToken

<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/admin-accountpool.png" />

#### 用户管理

支持用户管理

支持注册新用户

<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/admin-usermanage.png" />





