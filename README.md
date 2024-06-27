<div align="center">
  
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/LOGO.png" alt="Logo" width="100">

[![下载 Download](https://img.shields.io/github/downloads/Chenyme/oaifree-tools/total.svg?style=flat-square)](https://github.com/Chenyme/oaifree-tools/releases)
![Docker Pulls](https://img.shields.io/docker/pulls/chenyme/oaifree-tool)
![GitHub Repo stars](https://img.shields.io/github/stars/chenyme/oaifree-tools)


</div>

## 项目功能
> - 支持个性化管理站点
> - 支持账户密码-Oauth安全跳转
> - 支持用户注册、用户管理、Token管理
> - 支持手动/自动刷新AccessToken无需定时维护



## 部署项目
#### Docker
```
docker pull chenyme/oait:v1.01
docker run -d -p 8501:8501 chenyme/oait:v1.01
```

默认管理账号：**admin**，管理密码：**12345678**

**首次登录请及时修改账户密码，以及对应的邀请码**
