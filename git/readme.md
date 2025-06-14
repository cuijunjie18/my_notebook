# git 使用指南

## 背景

由于常用功能较为简单，仅记录最近新功能及出现问题的操作.

## git基础知识

- 本地仓库进行版本控制的流程
  
  ```shell
  git init # 初始化本地仓库
  git status # 查看文件追踪状态
  git add [file]  # 添加单个文件
  git add . # 可全部添加进暂时存储区或添加指定文件
  git commit -m "name" # 提交版本到本地仓库,并存下记录
  git log # 查看本题仓库的版本号记录
  git reset --hard [对应版本号记录的前六位字符] # 回到对应版本
  ```

- 分支管理问题
  我对分支的理解即让不同人在不同的分支进行操作,修改,各分支的内容不干扰(当然刚刚创建分支的时候,上一分支的内容会复制到当前新建分支)，可以在各自的分支进行各自的版本控制最后完成项目的时候可以把各个分支的任务合并到主分支中.
  ```shell
  git branch # 查看分支,*号所在即当前工作分支
  git checkout [分支标签] # 切换分支
  git checkout -b [分支标签] # 新建并切换到新分支
  git merge [分支名] # 把分支名对应分支合并到当前分支
  ```
  
- 远程仓库相关(重难点)
  首先本地仓库能够与远程仓库建立起来,需要对应远程仓库github账号上有本地的ssh密钥.
  
  ```shell
  git remote -v  # 查看当前连接的远程仓库,得到的是名称 + URL,名称为对应URL在本地的标识
  git remote  # 查看本地远程标识名称
  git remote add [本地远程标识名称] URl # 添加本地仓库中包含的远程仓库
  git push -u [本地远程标识符] 本地分支名 # 注意,对于远程没有对应分支名的,会在远程生成一个同名分支
                                      # 但是如果远程有相同的分支名,大概率会失败,因为文件不同步,所有这时候要先clone对应远程仓库使得本地与远程同步
                                      # 远程没有对应分支的时候,要-u新建,有了后不用-u
                                     
  git pull [本地远程标识] [远程分支名] # 当远程修改了文件,本地没有记录,所有先获取远程的修改记录(可log查看),并把远端的修改合并到当前本地分支(是合并,不是覆盖)
                                    # 之后push本地内容就会覆盖掉远端内容了(因为git中存了记录,即使覆盖有bug也可以reset)
  git fectch  # 现在不太理解,好像是只能为远端创建一个更新记录,但是未同步到本地

  git push --delete origin oldName # 删除远程的分支
  
  git clone --branch <branchname> <remote-repo-url>  #  克隆远程指定分支
  ```

- 补充
  git可以回退与前进各个版本
  查看历史版本：
  ```shell
  git reflog
  ```

## git进阶问题

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

