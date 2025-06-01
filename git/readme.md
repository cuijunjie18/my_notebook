## git 使用指南

### 背景

由于常用功能较为简单，仅记录最近新功能及出现问题的操作.


### git 提交

虽然这个用法已经经常用了，但是最近发现问题，在服务器上通过ssh无法push和clone，而通过http则可正常地push和clone.但是Linux系统仅可以通过ssh进行push操作，这就要求我们去解决这个问题.

推测：因为http可以正常使用，因为已经在服务器上执行过了反向代理操作，确保了http、https是走代理的，那么问题大概率是ssh没有走代理.

- 测试一般的ssh是否可用

    ```shell
    ssh -i ~/.ssh/id_rsa -T git@github.com
    # -i 表示提供认证file
    ```

    如果成功则会输出类似下面的信息
    ```shell
    Hi cuijunjie18! You've successfully authenticated, but GitHub does not provide shell access.
    ```

- 否则手动执行下面操作，让ssh走代理
    ```shell
    ssh -o "ProxyCommand=nc -X 5 -x 127.0.0.1:50001 %h %p" -i ~/.ssh/id_rsa -T git@github.com
    ```

  发现成功即可.如果还是不行，尝试执行下面的操作

    ```shell
    vim ~/.ssh/config
    ```

    写入
    ```vim
    Host github.com
        Hostname ssh.github.com
        User git
        IdentityFile ~/.ssh/id_rsa  # 确保路径与密钥匹配
        Port 443  # 默认端口
    ```

    这时候再次执行
    ```shell
    ssh -o "ProxyCommand=nc -X 5 -x 127.0.0.1:50001 %h %p" -i ~/.ssh/id_rsa -T git@github.com
    ```

- 或者不修改~/.ssh/config，直接通过命令行指定
  ```shell
  ssh -o "ProxyCommand=nc -X 5 -x 127.0.0.1:50001 %h %p" -i ~/.ssh/id_rsa -T -p 443 git@ssh.github.com
  ```


- 当可以通过ssh连接上github后，便可以push了，具体操作如下
  修改~/.ssh/config
  ```vim
  Host github.com
    HostName ssh.github.com
    User git
    Port 443
    IdentityFile ~/.ssh/id_rsa
    ProxyCommand nc -X 5 -x 127.0.0.1:50001 %h %p
  ```
  然后即可
  ```shell
  git push origin master
  ```

**注意：上面的过程如果想看详细信息，均可在ssh后加 -v**

**总结核心问题：**
- 端口Port
- 域名git@github.com与git@ssh.github.com
- ssh代理

### stash操作

```shell
git stash # 回去最近提交的状态，并保存当前工作状态
git stash pop # 回到之前保存的工作状态
```

### switch操作

```shell
git clone <url>
git branch --all
git switch -c <local_branch> <remote_branch>
```

### clone操作

当远程仓库的history过于庞大时，可以指定clone包含的history次数

```shell
git clone --depth <n> <repository-url>
```

### .gitignore的使用

当我们追踪了一次文件，或者叫提交了一次未被ignore的文件后，再在.gitignore文件里忽略它，这时候是不起作用的

我们需要运行下面的命令

```shell
git rm --cache filename
```

然后再提交，，就会发现不再追踪该文件.

