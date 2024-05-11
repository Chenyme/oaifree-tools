# oaifree-tools

[![下载 Download](https://img.shields.io/github/downloads/Chenyme/oaifree-tools/total.svg?style=flat-square)](https://github.com/Chenyme/oaifree-tools/releases)
![Docker Pulls](https://img.shields.io/docker/pulls/chenyme/oaifree-tool)


这是一个小白写的服务，如有不对之处还请指教。

演示站：[Demo](http://120.27.227.138:8501/)
（请不要修改演示站的superkey，谢谢❤️）

管理密码：neo_niubi

#### 如果你觉得有用请给我一个star🌟叭！


## 项目功能
> - 支持无域名部署（用始皇的网页）
> - 支持账户密码登录
> - 支持注册码注册
> - 支持Oauth直接跳转
> - 支持用户管理，token管理
> - 支持用户自己刷新token，无需自己维护

## 最近更新
> - 新ui
> - 修复了一些已知问题


## 效果图

### 主界面

![2](https://github.com/Chenyme/oaifree-tools/blob/main/public/v31.png)

### 管理界面

![2](https://github.com/Chenyme/oaifree-tools/blob/main/public/v33.png)

### 用户界面

![2](https://github.com/Chenyme/oaifree-tools/blob/main/public/v32.png)


### 如何安装

- 首先你需要一台VPS，准备好docker。
- 然后在服务器中输入```docker pull chenyme/oaifree-tool:v2```等待镜像拉取。
- 拉取完后```docker run -d -p 8501:8501 chenyme/oaifree-tool:v2```（记得打开服务器的8501端口）。
- 最后在网页中输入`服务器IP:8501`就能访问啦。
- 看到和上面的效果图一样的界面就是成功了


## 如何使用

### 配置参数

1. 首次登录服务请点击`More Options`选择`admin`，默认密码为`neo_niubi`

![2](https://github.com/Chenyme/oaifree-tools/blob/main/public/2.png)


2. **接着请先修改superkey！！！**，然后可以更改域名，默认为始皇的域名

![3](https://github.com/Chenyme/oaifree-tools/blob/main/public/3.png)


3. 在账户管理里面输入你的账户信息和各类token

![4](https://github.com/Chenyme/oaifree-tools/blob/main/public/4.png)


4. 用户注册可以直接创建用户 

![6](https://github.com/Chenyme/oaifree-tools/blob/main/public/6.png)


5. 用户管理可以删除用户和修改用户密码

![7](https://github.com/Chenyme/oaifree-tools/blob/main/public/7.png)


6. 支持刷新access-token

![5](https://github.com/Chenyme/oaifree-tools/blob/main/public/5.png)


7. 支持用户自主维护刷新

![8](https://github.com/Chenyme/oaifree-tools/blob/main/public/8.png)

### 使用网站
1. 输入用户名。
2. 输入密码。
3. 点击`LOGIN`, 等待新按钮出现。
4. 点击`Click To Verify`，直接访问。

![9](https://github.com/Chenyme/oaifree-tools/blob/main/public/9.png)

### 用户邀请
1. 开启注册功能，设置注册码

![11](https://github.com/Chenyme/oaifree-tools/blob/main/public/11.png)
  
2. 注册

![12](https://github.com/Chenyme/oaifree-tools/blob/main/public/12.png)

## 鸣谢

### 感谢始皇的付出，让我们能真正的使用这些服务！
### 我是个小白，所有服务都是基于本地实现的，然后框架也是用的streamlit，因为不会写前端，如果有不足之处还请轻点骂。
### 如果你觉得有用请给我一个star叭！

[My Linux.do](https://linux.do/t/topic/63194)
