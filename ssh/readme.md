### ssh : 远程连接、服务器搭建必备

openssh官网 : https://www.openssh.com/

#### 背景

要想使用ssh,需要先查看我们的系统是否有ssh服务了(通常情况是指开源的openssh软件包)  

通过下面指令查找

```shell
dpkg -l | grep ssh
```

得到下面的内容
![查找openssh](images/a.png)

如果openssh-client与openssh-server即可跳到[使用阶段](#ssh_use)，否则继续下面的[安装过程](#ssh_install).

#### openssh安装与启动

<span id="ssh_install"></span>

通常来说，有openssh-client即可远程连接服务器，但是要有openssh-server才能让本机成为服务器.

- 直接执行下面指令

    ```shell
    # 先更新软件包
    sudo apt update
    ```

    ```shell
    # openssh的安装
    sudo apt-get install openssh-client
    sudo apt-get install openssh-server
    ```

    ```shell
    # 再次查看openssh是否成功安装
    dpkg -l | grep ssh
    ```

- 检查服务是否开启.

    使用下面的指令

    ```shell
    ps -ef | grep sshd
    ```

    出现以下信息即可
    ![](images/b.png)
    即进程<strong>/usr/sbin/sshd</strong>成功开启.

    或者使用下面的指令

    ```shell
    systemctl status sshd 
    stemctl status ssh
    # 上面两条指令等价，都查看ssh.service
    ```

    得到类型以下的信息即可

    ![](images/c.png)

- 为服务设置开启自启动

    ```shell
    sudo systemctl enable ssh
    ```

- 查看是否成功开机自启动

    ```shell
    systemctl is-enabled ssh
    ```

    或者下面的指令

    ```shell
    systemctl list-unit-files --type=service    --state=enabled | grep ssh 
    ```

    得到结果显示enable即可.


#### ssh的使用

<span id="ssh_use"></span>

- 已知服务器ip及用户，直接连接
  
  ```shell
    ssh -p <端口> username@<server_computer_ip> 
  ```

  提示输入密码即可连接.  

- 免密连接
  
  先本地产生公钥、私钥.

  ```shell
  ssh-keygen -t rsa   #-t表示类型选项，这里采用rsa加密算法
  ```

  我们会在本地的 ~/.ssh下看到如下文件目录

  ```shell
    ├── config
    ├── id_rsa
    ├── id_rsa.pub
    ├── known_hosts
    └── known_hosts.old
  ```
  其中，id_rsa即私钥、id_rsa.pub即公钥，我们将id_rsa.pub复制到服务器上的<strong>/home/user/.ssh/authorized_keys</strong>即可面密登陆.
  <br/>

- 通过<strong>~/.ssh/config</strong>文件简易登陆
    
    该文件的内容如下

  ```shell
    Host <name>
	    HostName <computer_ip>
	    Port <port_id>
	    User <user_name>
        IdentityFile ~/.ssh/id_rsa
  ```

  配置了服务器的信息后，即可直接如下指令连接

  ```shell
    ssh <name>
  ```

#### 后记

不足与代补充处欢迎提issue！
