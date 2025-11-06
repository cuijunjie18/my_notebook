# GDB调试工具使用

## 目录

[gdb配置](#美化配置)  
[使用案例](#具体案例)  

<br>

## 美化配置

### gdb dashboard安装

由于原始 GDB 命令行过于简陋，为方便调试，我们需要下载 gdb-dashboard 插件

参考官网安装教程：https://github.com/cyrus-and/gdb-dashboard

启用语法高亮，需要安装pygments的python包
```shell
pip install --no-cache-dir pygments
```

**注意如果不生效，执行下面的命令**
```shell
grep -qxF 'set auto-load safe-path /' ~/.gdbinit || echo 'set auto-load safe-path /' >> ~/.gdbinit # 使gdb可以信任所有目录的.gdbinit
```

- 在gdb中查看dashboard的使用
  进入gdb后，执行
  ```shell
  help dashboard
  ```
  如果输出信息，说明dashboard成功安装，后续run即可自动显示

<br>

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

  <br>

## 带命令参数的调试


命令格式
```shell
gdb --args ./program arg1 arg2 arg3
```

可以使用下面的demo代码调试带参数、段错误
```cpp
#include <bits/stdc++.h>

using namespace std;

int main(int argc,char *argv[]){
    std::cout << argc << "\n";
    for (int i = 0; i < argc; i++){
        std::cout << argv[i] << "\n";
    }
    int *p = nullptr;
    std::cout << *p << "\n";
    return 0;
}
```

demo尝试
```shell
g++ -g -o demo demo.cpp
gdb --args ./demo 123 456 789
run # 直到段错误
bt  # 查看函数调用栈
```

<br>

## 参考

调试core dump： https://zhuanlan.zhihu.com/p/1894779801983767813  
简单使用： https://blog.csdn.net/weixin_45031801/article/details/134399664  