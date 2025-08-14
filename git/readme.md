# git 使用指南

## 背景

由于常用功能较为简单，仅记录最近新功能及出现问题的操作.

## 目录

[基础知识](#git基础知识)  
[进阶操作](#git进阶问题)  
[具体案例](#具体案例)  

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
  git branch --all # 查看分支,*号所在即当前工作分支
  git branch --delete branchname # 删除分支
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

### 目录

[git提交](#git-提交)  
[clone操作](#clone操作)  
[stash操作](#stash操作)  
[switch操作](#switch操作)  
[.gitignore使用](#gitignore的使用)  
[gitlfs相关](#git下载大文件使用git--lfs)   
[git默认GUI](#git的gui默认编辑器设置)  
[git删除本地历史记录](#git-删除本地历史记录)  

<br>

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

<br>

### stash操作

通常适用于临时改项目，但是突然要上线可用的版本，那就stash回到之前可用的版本，同时保存当前的工作，等项目结束后在pop继续改.

```shell
git stash # 回去最近提交的状态，并保存当前工作状态
git stash pop # 回到之前保存的工作状态
```
<br>

### switch操作

通常适用于clone后切换到本地指定分支，但是一般会默认到本地master分支

```shell
git clone <url>
git branch --all
git switch -c <local_branch> <remote_branch>
```

<br>

### clone操作

当远程仓库的history过于庞大时，可以指定clone包含的history次数

```shell
git clone --depth <n> <repository-url>
```

<br>

### .gitignore的使用

当我们追踪了一次文件，或者叫提交了一次未被ignore的文件后，再在.gitignore文件里忽略它，这时候是不起作用的

我们需要运行下面的命令

```shell
git rm --cache filename
```

然后再提交，，就会发现不再追踪该文件.

<br>

### git下载大文件——使用git -lfs

背景：在hugging-face下载数据集，通过clone的形式，如果没有git-lfs,仅能下载到指向文件的pointer.

huggingface-mirror： https://hf-mirror.com

- 先在git-lfs官网将Linux软件包源添加到本地 
   
  官网教程：https://git-lfs.github.com/

  ```shell
  curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
  ```

- 安装gif-lfs本体
  ```shell
  sudo apt-get install git-lfs
  git lfs install #  初始化Git LFS
  ```

<br>

### git的GUI默认编辑器设置

有些服务器的git GUI的默认编辑器是nano，不太习惯，可设置为vim

```shell
git config core.editor vim
```
<br>


### git 删除本地历史记录

```shell
git log # 找到要删除记录的前一个记录hash_id
git rebase -i <hash_id>
# pick 改为 drop即可
```

<br>

## 具体案例

### 目录

[git本地仓库意外丢失](#git本地仓库意外丢失)   
[git误交大文件](#git误交大文件)    
[git提交大文件](#git提交大文件)  
[git团队协作](#git团队协作pull-request)  
[git配置代理](#git配置代理)  
[clone私有仓库](#clone私有仓库)  

### git本地仓库意外丢失

丢失原因： 可能因为追踪并提交了大文件等各种原因，目前又不会处理，然后push不了.

总之，如果.git文件无了，那么下面操作.

- 重新初始化
  ```shell
  rm -rf .git
  git init
  git remote add origin <url>
  git add .
  git commit -m xxxx
  git push origin master
  ```
  但是这样一般是交不上去的(虽然可以处理，但是十分复杂)，因为新仓库丢失了太多之前远程仓库的信息.

- 备份、clone、重交组合拳
  ```shell
  cd new_dir
  git clone <url>
  git switch -c <local_branch> <remote_branch> # 复制远程分支到本地分支(通常会自动绑定本地master到远程的default分支)
  cd <url的仓库>
  rm -rf ./*  # 删除全部文件
  cp -r backup/* . # 复制.git没了的崩溃仓库文件.
  ```

  即可重新提交了.
  ```shell
  git status
  git add .
  git commit -m xxx
  git push origin <now_branch>
  ```

<br>

### git误交大文件

不小心track了大文件，且本地commit了，然后push出现下面的问题.

![](images/a.png)


错误做法： 

```shell
git rm big-file
git add .
git commit "remove big-file"
git push origin master
```
哪怕使用git rm --cached big-file都没用.  
问题依旧没有解决，因为git是基于历史记录工作的，需要对历史记录进行操作.

正常做法：
```shell
# git config core.editor vim # 先设置默认编辑器
git log # 找到大文件提交的前一个记录
git rebase -i <commit_hash> # 一般是前6位
```
注意找的不是当前大文件提交的记录hash，而是前一个!

进入的界面如下:

![](images/b.png)

操作如下
```shell
# 将对应大文件记录的pick -> edit
pick -> edit
# pick -> drop 即删除本地记录，等价于reset，一般不用
```

退出后，终端出现下面的提示

```shell
Stopped at 005ae66...  3
You can amend the commit now, with

  git commit --amend 

Once you are satisfied with your changes, run

  git rebase --continue
```

此时处于git编辑模式，执行
```shell
git rm --cached big-file # 在编辑模式下删除大文件
git rebase --continue # 完成变基，可能会进入vim,保存退出即可.
```
这时候便能正常
```shell
git push origin master
```

同时这些提交不影响和big-file一起提交的其他文件，本质原理是对历史记录进行了修改.

最后给一张完整操作结果图
![](images/demo.png)

参考文章：
- https://xmanyou.com/how-to-revert-commit-with-large-file/
- https://medium.com/analytics-vidhya/tutorial-removing-large-files-from-git-78dbf4cf83a

<br>

### git团队协作——pull request

如果有一个开源仓库，我想要加入开发并成为contributor,那么就需要create pull request，并让作者满意.

团队协作流程

注：有两种形式的协作开发，一种是内部团体开发，这种的可以将开发分支命名为个人id，可直接提交；另一种是开源的，这种就需要fork，这时候的原开源仓库就叫做上游仓库，在本地修改完后即可对上游仓库提pr(即pull request)

- clone或者fork开源仓库
  ```shell
  git clone <url>
  ```
- 新建develop分支对**远程感兴趣分支**进行二次开发
  ```shell
  # 下面指令二选一
  git checkout -b dev origin/<branch_name> 
  git switch -c dev origin/<branch_name>
  ```

- 代码开发
- (可选)同步远程log，适用于内部团队开发
  ```shell
  git fetch
  ```

- 提交开发分支
  ```shell
  git commit -m "demo"
  git push origin dev
  ```

- 提出pull request
  直接在github上提交即可.

那么github上接受了pr，作者本地的对应分支如何同步呢?同步了是否会丢失本地的文件呢?
- 同步
  ```shell
  git fetch # 获取最新的记录
  git checkout <接受pr的本地分支> # 假设为master
  git merge master origin/master
  ```

- 本地文件问题
  除非接受了删除的文件，否则本地的其余文件不会丢失.

参考文章：
- https://zhuanlan.zhihu.com/p/672447698


### git提交大文件

git提交大文件需要使用git-lfs，参考官网使用： https://git-lfs.com/

- 下载git-lfs(**建议每次提交前执行一次**)
  ```shell
  git lfs install
  ```

- 追踪大文件
  ```shell
  git lfs track "*.zip"
  ```

- 确保.gitattributes被追踪
  ```shell
  git add .gitattributes
  ```

- 追踪大文件并提交
  ```shell
  git add file.zip
  git commit -m "Add design file"
  git push origin main
  ```

成功会出现下面的上传过程
![git-lfs上传](images/c.png)


### git配置代理

这里仅将如何为git配置http代理，ssh代理见[git提交](#git-提交)  

执行
```shell
git config --global http_proxy http://<url> # 如http://localhost:50001
git config --global https_proxy https://<url>
```

查看配置信息
```shell
git config --list
# 或者vim ~/.gitconfig
```

### clone私有仓库

一般而言，私有仓库clone将需要clone的本机ssh公钥放到个人github设置即可clone，如果不行，可以设置token使用https下载.

先在此界面获取token

![get tokens](images/token.png)

然后执行下面的clone
```shell
git clone https://<token_name>:<token>@github.com/<your_repository>
# 如下
git clone https://123:131212@github.com/cuijunjie18/HuaWei-Qwen2.5VL.git
```