# docker使用

## 目录

[安装](#ubuntu下docker安装)  
[具体例子](#具体案例)  

<br>

## Ubuntu下docker安装

csdn： https://blog.csdn.net/u011278722/article/details/137673353

- 添加用户到docker用户组
  ```shell
  sudo usermod -aG docker <user>
  ```

<br>

## 具体案例

[设置代理](#无法连接docker-hub)  
[运行容器](#运行一个容器)  
[vscode进入docker容器](#vscode进入docker容器)  
[打包项目](#docker打包项目)  

<br>

### 无法连接docker-hub

当执行下面的命令且本地没有镜像缓存的时候，会默认从远程仓库拉取
```shell
docker run hello-world
```
如果无法连接远程仓库，下面是解决方法

- 法一：设置代理
  ```shell
  sudo mkdir -p /etc/systemd/system/docker.service.d
  sudo vim /etc/systemd/system/docker.service.d/http-proxy.conf
  ```

  加入(注意替换为自己的代理)
  ```vim
  [Service]
  Environment="HTTP_PROXY=http://proxy.example.com:8080/"
  Environment="HTTPS_PROXY=http://proxy.example.com:8080/"
  Environment="NO_PROXY=localhost,127.0.0.1,.example.com"
  ```
  重新启动docker
  ```shell
  sudo systemctl daemon-reload
  sudo systemctl restart docker
  ```
  再次尝试即可.

- 法二：设置镜像站
    这边镜像站比较杂，一般推荐阿里云
    ```shell
    sudo vim /etc/docker/daemon.json
    ```

    添加(举个例子，不一定有效)
    ```vim
    {
      "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://registry.docker-cn.com"
      ]
    }
    ```

    重启
    ```shell
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    ```

<br>

### 运行一个容器

- 查看可用的镜像
  ```shell
  docker images
  ```

- 直接运行容器
  ```shell
  docker run -it <image_id> bash
  # 或者docker run -it <image_name> bash
  ```
  这样就会直接进入容器，
  但是这样每次ctrl + D或者exit退出容器，其中的数据都不存在了，需要后台执行

- 后台运行容器
  ```shell
  docker run -it -d <image_id> bash
  ```
  执行了这条命令后容器进入后台执行，需要显示进入
  ```shell
  docker container ls # 查看正在运行的容器
  docker exec -it <container_id> bash/zsh
  ```

- 如果已经以前台运行了一个容器，如何后台挂起
  ```shell
  # 在容器内按下组合键
  ctrl + P,ctrl + Q
  ```

<br>

### vscode进入docker容器

详见[vscode进入docker容器](vscode进入docker容器.md)

<br>

### docker打包项目

直接参考CSDN：https://blog.csdn.net/feifeiwud/article/details/126636051  
知乎：https://zhuanlan.zhihu.com/p/707459263

<br>

## 参考

csdn: https://blog.csdn.net/weixin_71699295/article/details/137387383

入门到实践： https://yeasy.gitbook.io/docker_practice  