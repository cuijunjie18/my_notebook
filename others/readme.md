# 杂项(未分类的)

## wget遇到证书认证问题

解决方案如下
```shell
wget --no-check-certificate <url>
```

## grep使用

- 查找文件夹内含某个字符串的文件
  ```shell
  grep <str> -r <dir>
  grep <str> -rl <dir> # 仅显示匹配的文件名，不给出具体匹配的位置
  ```

## 清理进程

- 清理全部相同名字的进程，如zsh进程过多
  ```shell
  ps -ef | grep zsh | awk '{print $2}' # 输出所有zsh进程的pid
  ps -ef | grep zsh | awk '{print $2}' | xargs kill -9 # 清理
  ```
  但是上面的命令依旧有问题，可能会kill掉grep这个指令，且kill当前tty里的zsh进程，修改如下
  ```shell
  ps -ef | grep zsh | grep -v grep # 这样就不会包括grep命令本身了
  ps -ef | grep zsh | grep -v grep | grep -v $$ # $$是一个特殊变量，表示当前shell会话的PID
  ```

## 一种可选择执行的bash脚本编写

```shell
#!/bin/bash

export PATH=$PATH:/mnt/data/workspace/obf_em/build/bin

echo $PATH | tr ':' '\n'
echo '================================='
echo $LD_LIBRARY_PATH | tr ':' '\n'
echo '================================='

while true; do
echo "Please choose what you run:"
echo "1. run to end"
echo "2. gdb the executable"
echo "3. normal demo"
read -r choice
case $choice in
        1)
            build/bin/execution-management -m build/configs/examples/machine.json -a build/configs/examples/app_folder_start_with_depend
            break
            ;;
        2)
            gdb --args build/bin/execution-management -m build/configs/examples/machine.json -a build/configs/examplesapp_folder_start_with_depend
            break
            ;;
        3) 
            build/scripts/start_execution_management_demo.sh
            break
            ;;
        *) echo "invalid option. Please try again"
            break
            ;;
    esac
done
```