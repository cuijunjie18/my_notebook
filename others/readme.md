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

## 统计某语言代码行数的脚本

```shell
#!/bin/bash
# 统计当前目录下所有 .c 和 .h 文件的行数总和
find . -type f \( -name "*.c" -o -name "*.h" \) -exec cat {} + | wc -l
```

解释如下
| 代码片段 | 含义 |
|:---|:---|
| `find .` | 从当前目录（`.`）开始递归搜索整个目录树。 |
| `-type f` | 仅匹配**普通文件**（排除目录、软链接、设备文件等）。 |
| `\( -name "*.c" -o -name "*.h" \)` | **条件分组**：<br>• `\(` 和 `\)` 是转义的圆括号，用于将多个条件组合，避免 shell 提前解析。<br>• `-name "*.c"` 匹配以 `.c` 结尾的文件。<br>• `-o` 表示逻辑“或”（OR）。<br>• 整体效果：匹配后缀为 `.c` **或** `.h` 的文件。 |
| `-exec cat {} +` | 对匹配到的文件执行 `cat` 命令：<br>• `{}` 是占位符，会被实际找到的文件路径替换。<br>• `+` 表示**批量追加**：`find` 会尽可能多地把文件名塞进同一条 `cat` 命令中执行（直到达到系统参数长度上限），比 `\;`（每个文件执行一次 `cat`）效率高几个数量级。 |
| `\|` | 管道符：将左侧 `cat` 输出的所有文件内容，作为右侧命令的标准输入。 |
| `wc -l` | `wc`（word count）的 `-l` 选项：**统计输入流中的换行符（`\n`）数量**，即总行数。 |