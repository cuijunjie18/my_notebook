### Ubuntu系统的一些常见修改及配置

#### 背景

如遇到重装Ubuntu系统，可能会有一些之前的配置忘记，故在此使用笔记的形式记录

#### 更换系统apt源

使用清华源：https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/

将下面的内容(清华源)替换<strong>/etc/apt/sources.list</strong>

**注意：要先执行下面指令备份原始的源后再替换.**

```shell
sudo cp /etc/apt/sources.list /etc/apt/sources.list.old 
```

```vim
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse

# 以下安全更新软件源包含了官方源与镜像站配置，如有需要可自行修改注释切换
deb http://security.ubuntu.com/ubuntu/ jammy-security main restricted universe multiverse
# deb-src http://security.ubuntu.com/ubuntu/ jammy-security main restricted universe multiverse

# 预发布软件源，不建议启用
# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-proposed main restricted universe multiverse
# # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-proposed main restricted universe multiverse
```

#### 设置系统restart等待时间

Ubuntu restart默认时间是**1min30s**，有时候我们需要频繁切换系统，这会给我们带来不必要的时间消耗，我们可以执行下面的操作来修改默认的重启等待时间.

```shell
cd /etc/systemd
sudo vim system.conf
```

![](images/a.png)
然后打开注释这两行的注释并修改时间即可.

#### Ubuntu系统内置时间

有时候发现切换系统后Ubuntu的Auto time set不起作用，换一个wifi即可解决.