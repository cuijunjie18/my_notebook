# 杂项

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