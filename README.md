<div align="center">
  
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/LOGO.png" alt="Logo" width="100">

![GitHub License](https://img.shields.io/github/license/chenyme/oaifree-tools)
![Docker Image Size](https://img.shields.io/docker/image-size/chenyme/oait)
![Docker Image Version](https://img.shields.io/docker/v/chenyme/oait)
![GitHub Repo stars](https://img.shields.io/github/stars/chenyme/oaifree-tools)


</div>

## 项目功能
> - 支持多种个性化设置。
> - 支持账户密码-Oauth安全跳转。
> - 支持号池管理、用户管理、域名管理。
> - 支持OpenAI的最新UI、Classic经典UI。
> - 支持手动/自动刷新AC_Token状态。
> - 支持自动检测用户SA_Token状态并刷新。
> - 支持刷新令牌、邀请令牌，实现自助发卡维护。

## 项目部署
#### docker
```shell
docker pull chenyme/oait:v1.1.1
docker run -d -p 8501:8501 chenyme/oait:v1.1.1

# docker pull ghcr.io/chenyme/oait:latest
# docker run -d -p 8501:8501 ghcr.io/chenyme/oait:latest
```

#### Git
```shell
git clone https://github.com/Chenyme/oaifree-tools
docker build -t chenyme/oait:v1.1.1 .
docker run -d -p 8501:8501 chenyme/oait:v1.1.1
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
docker pull chenyme/oait:v1.1.1
docker run -d -p 8501:8501 chenyme/oait:v1.1.1

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





