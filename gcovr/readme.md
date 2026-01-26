# python包——gcovr使用

## 背景

Gcovr 提供了一个用于管理 GNU gcov 工具使用并生成汇总代码覆盖率结果的实用程序。

## 安装

```shell
pip install gcovr
```

## 使用

- 以下面的demo源码为例子
    ```cpp
    #include <iostream>
    using namespace std;

    void func1() {
        std::cout << "1" << std::endl;
        return;
    }

    void func2() {
        std::cout << "2" << std::endl;
        return;
    }

    int main() {
        std::cout << "Hello,World!" << std::endl;
        func1();
        return 0;
    }
    ```

- 编译
    ```shell
    g++ -fprofile-arcs -ftest-coverage -O0 -g main.cpp -o main
    # 其中 -fprofile-arcs -ftest-coverage是gcovr的核心编译指令，-O0是为了防止编译器优化，导致统计覆盖率出问题
    ```

- 执行程序
    ```shell
    ./main
    ```
    会在当前目录下生成<strong>.gcda文件</strong>，表示对程序执行一次测试

- 绘制覆盖信息
    ```shell
    gcovr -r .
    ```

- 生成html可视化结果
    ```shell
    gcovr -r . --html --html-details -o your_dir/example-html-details.html
    ```

效果如下：
![a](images/a.png)  
![b](images/b.png)  

## 参考

简单使用：https://www.cnblogs.com/KID-XiaoYuan/p/13266700.html  
官方说明：https://gcovr.com/en/stable/index.html

