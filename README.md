<div align="center">
  
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/LOGO.png" alt="Logo" width="100">

![GitHub License](https://img.shields.io/github/license/chenyme/oaifree-tools)
![Docker Image Size](https://img.shields.io/docker/image-size/chenyme/oait)
![Docker Image Version](https://img.shields.io/docker/v/chenyme/oait)
![GitHub Repo stars](https://img.shields.io/github/stars/chenyme/oaifree-tools)


</div>

## 写在前面
#### 这是一个 oaifree/pandora/fuclaude 后台管理项目，所有数据采用本地存储，登录系统、后台管理、共享服务、自动刷新 等逻辑完全纯手搓，如有错误还请见谅，供娱乐交流。
#### 本人是个小菜鸡，仅会 python 和 C ，不太会前端，因此使用 Streamlit 作为框架，还请别喷我！！！



> [!NOTE]
> 本项目为开源项目，使用者必须在遵循 OpenAI 和 Claude 的 **使用条款** 以及 **法律法规** 的情况下使用，不得用于非法用途。
> 
> 根据[**《生成式人工智能服务管理暂行办法》**](http://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)的要求，请勿对中国地区公众提供一切未经备案的生成式人工智能服务。

> [!WARNING]
> 首次登录请**及时修改账户密码**！
> 
> **默认管理账号：`admin`， 管理密码：`12345678`**

> [!WARNING]
> **Demo站：[OaiT_Demo](https://oait_demo.chenyme.top/), 请勿修改Demo站的账户密码，或填入敏感信息！**
>
> **账号：`linux.do`， 密码：`linux.do`**



## 项目功能
  - **支持始皇所有的服务**：Pandora/Oaifree/Fuclaude
  - **登录支持**：支持接入 linux.do 登录/ UID登录
  - **服务总览**：服务统计/图表数据/站点迁移/运行日志
  - **域名管理**：域名列表/服务切换/延迟测速/自定义域名
  - **主题样式**：管理信息/网站设置/主题切换/公告设置
  - **号池管理**：账号总览/账号刷新/邀请令牌/刷新令牌
  - **用户管理**：用户总览/用户注册/Oaifree/Fucluade
  - **更多功能**：共享服务/Oai-APi（暂未开发）/关于项目

## 项目部署

#### docker
```shell
docker pull chenyme/oait:v1.2.1
docker run -d -p 8501:8501 chenyme/oait:v1.2.1

# docker pull ghcr.io/chenyme/oait:latest
# docker run -d -p 8501:8501 ghcr.io/chenyme/oait:latest
```

#### Git
```shell
git clone https://github.com/Chenyme/oaifree-tools
docker build -t chenyme/oait:v1.2.1 .
docker run -d -p 8501:8501 chenyme/oait:v1.2.1
```

#### Python
```shell
git clone https://github.com/Chenyme/oaifree-tools
cd oaifree-tools
streamlit run home.py
```

## 更新/迁移

> **V1.2.0为了适配fuclaude，很多配置进行了重构，因此之前的版本不支持自动迁移，请手动更改数据迁移！**

1. 登录原服务器项目管理后台，在`服务总览`- `站点迁移` 下导出所有配置文件

2. 在服务器上运行命令

```shell
docker pull chenyme/oait:v1.2.0
docker run -d -p 8501:8501 chenyme/oait:v1.2.0

# docker pull ghcr.io/chenyme/oait:latest
# docker run -d -p 8501:8501 ghcr.io/chenyme/oait:latest
```

3. 登录新服务器项目管理后台，在`服务总览`- `站点迁移` 下导入所有配置文件


## 主要功能介绍

#### 登录系统

- [x] 用户注册
- [x] 修改密码
- [x] UID登录
- [x] Oauth登录
- [x] 账户续费
- [x] 主题切换
- [x] UID 一键登录
- [x] Oauth登录，防止Token泄露
- [x] 管理员 首页登录 / 管理员界面登录
- [x] 自动刷新AC/SA Token

#### 后台管理
- [x] 安全保护
- [x] 令牌管理
- [x] 共享管理
- [x] 主题切换、编辑公告
- [x] 服务总览、日志记录
- [x] 数据导出、站点迁移
- [x] 号池管理、刷新Token
- [x] 用户管理、注册用户
- [x] 服务域名管理、站点限制
- [x] 服务状态刷新、用户状态刷新


## 项目预览

#### 登录界面
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/Theme3.png" />

#### UID 登录
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/UID.png" />

#### 更改密码
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/Change.png" />

#### 账户续费
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/Refresh.png" />

#### 共享服务
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/Share.png" />

#### 后台登录
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/Admin.png" />

#### 服务总览
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/服务总览.png" />

#### 域名管理
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/域名管理.png" />

#### 主题样式
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/主题样式.png" />

#### 账号总览
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/账号总览.png" />

#### 邀请令牌
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/邀请令牌.png" />

#### 刷新令牌   
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/刷新令牌.png" />

#### 用户总览  
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/用户总览.png" />

#### Oaifree  
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/Oaifree.png" />

#### Fuclaude
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/Fuclaude.png" />

#### 共享服务
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/共享服务.png" />

#### 关于项目
<img src="https://github.com/Chenyme/oaifree-tools/blob/main/public/关于项目.png" />






