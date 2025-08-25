# Linux定时任务——crontab

## 背景

对于需要做一些自动化部署及检查任务，需要Linux定时执行某些进程，这里推荐使用crontab

## crontab使用

### 基本使用

```shell
crontab [-u username]　# 省略用户表表示操作当前用户的crontab
    -e      (编辑工作表)
    -l      (列出工作表里的命令)
    -r      (删除工作表)
```

我们用crontab -e进入当前用户的工作表编辑，是常见的vim界面。每行是一条命令.

crontab的命令构成为 时间+动作，其时间有分、时、日、月、周五种，操作符有

- \* 取值范围内的所有数字
- / 每过多少个数字
- \- 从X到Z
- ，散列数字

**命令的标准格式说明**
```vim
# m h dom mon dow command
* * * * * command_to_be_executed
- - - - -
| | | | |
| | | | +----- 星期几 (0 - 7) (星期天为 0 或 7)
| | | +------- 月份 (1 - 12)
| | +--------- 日期 (1 - 31)
| +----------- 小时 (0 - 23)
+------------- 分钟 (0 - 59)
```

### 注意事项

- Cron 执行任务的环境与你的用户 Shell 环境不同，它非常精简。因此，对于脚本中的命令，最好使用绝对路径（如 /usr/bin/curl 而不是 curl），或者在脚本开头自行设置 PATH 环境变量.
    <br>
- 确保Cron的脚本具有可执行权限
  ```shell
  chmod +x <your_script>
  ```

### 调试技巧

- 查看对应脚本的日志
  ```shell
  sudo grep <your_script_name> /var/log/syslog 
  ```
  查看是否按规定的时间运行了
    <br>

- 查看cron的日志
  ```shell
  sudo grep CRON /var/log/syslog
  ```
    <br>
    
- 查看cron服务信息
  ```shell
  sudo systemctl status cron
  ```
  服务信息里会包含对应脚本的执行信息

## 参考文章

- 菜鸟：https://www.runoob.com/w3cnote/linux-crontab-tasks.html  
- 知乎：https://zhuanlan.zhihu.com/p/680738656  