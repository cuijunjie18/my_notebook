# GDB调试工具使用

## 具体案例

### 调试core dump

core dump是程序崩溃前保存的**快照**，用于调试.

- 查看是否会生成core文件
  ```shell
  ulimit -c # 输出0则不会
  ```

- 设置生成core文件
  ```shell
  ulimit -c unlimited
  sudo sh -c "echo './core' > /proc/sys/kernel/core_pattern"  # 修改默认生成位置
  ```
  如果不修改默认生成位置，使用下面的指令查看当前core文件的生成位置
  ```shell
  cat /proc/sys/kernel/core_pattern
  ```

- 调试core文件
  ```shell
  gdb ./program <core_file>
  # bt查看函数调用栈、f <n>跳转到对应的函数栈
  ```
  具体效果如下(一个空指针错误例子)
  ![empty_ptr](images/a.png)  


## 参考

https://zhuanlan.zhihu.com/p/1894779801983767813