# docker使用

## Ubuntu下docker安装

csdn： https://blog.csdn.net/u011278722/article/details/137673353

## 具体案例

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

## 参考

csdn: https://blog.csdn.net/weixin_71699295/article/details/137387383

入门到实践： https://yeasy.gitbook.io/docker_practice  