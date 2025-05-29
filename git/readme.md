### git 使用指南

#### 背景

由于常用功能较为简单，仅记录最近新功能

#### stash

```shell
git stash # 回去最近提交的状态，并保存当前工作状态
git stash pop # 回到之前保存的工作状态
```

#### switch

```shell
git clone <url>
git branch --all
git switch -c <local_branch> <remote_branch>
```

#### clone

当远程仓库的history过于庞大时，可以指定clone包含的history次数

```shell
git clone --depth <n> <repository-url>
```

#### .gitignore

当我们追踪了一次文件，或者叫提交了一次未被ignore的文件后，再在.gitignore文件里忽略它，这时候是不起作用的

我们需要运行下面的命令

```shell
git rm --cache filename
```

然后再提交，，就会发现不再追踪该文件.