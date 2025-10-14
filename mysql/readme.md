# mysql数据库

## 背景

想开发一台高性能web服务器，发现数据库这部分的知识空白，便学习一下

## 目录

[安装](#mysql数据库安装)  
[基本使用](#mysql数据库基本使用)  
[cmake使用sql](#cmake使用sql)  
[参考](#参考)  

## mysql数据库安装

本文为linux系统，型号如下
```shell
Linux cjj-HKF-WXX 6.8.0-65-generic #68~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Tue Jul 15 18:06:34 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
```

下面是安装流程。

- 更新apt包
  ```shell
  sudo apt update
  ```

- 安装mysql-server
  ```shell
  sudo apt install mysql-server 
  ```

- 启动服务并配置开机自启动
  ```shell
  sudo systemctl start mysql
  sudo systemctl enable mysql
  ```   

- 检查状态
  ```shell
  sudo systemctl status mysql
  ```

本地安装好MySQL后，系统会自动配置好登陆密码，本地登陆MySQL可以在不输入密码的情况下完成(默认仅能root用户登陆).

**注意：上面的安装仅是MySQL 服务器程序，不包含开发所需的头文件，为了以后能在c++中调用相关的API，需要安装MySQL的开发包**

```shell
sudo apt update
sudo apt install libmysqlclient-dev
```

验证库和头文件的安装
```shell
# 检查头文件
find /usr -name "mysql.h" 2>/dev/null

# 检查库文件
find /usr -name "libmysqlclient*" 2>/dev/null
```

## mysql数据库基本使用

[基本操作](#mysql数据库基本使用)  
[用户操作](#mysql用户基本操作)  
[database操作](#数据库数据操作)  

### 数据库基本操作

- 使用root用户登陆(确保mysql服务开启)
  ```shell
  sudo mysql
  # exit 指令退出
  ```

  为root @ localhost设置密码
  ```shell
  alter user root@localhost identified with mysql_native_password by <new_passwd>;
  ```

  之后就不能直接sudo登陆了，需要使用[用户登陆](#mysql用户基本操作)

- 查看数据库
  ```shell
  show databases; # 查看全部已创建的数据库
  select database(); # 查看当前运行的数据库
  ```

- 数据库的创建与删除
  ```shell
  create database <database_name>; # 创建数据库
  drop database <database_name>; # 删除数据库
  ```

- 数据库的使用、切换
  ```shell
  use <database_name>;
  select database(); # 查看当前运行的数据库，在<database_name>
  ```

### mysql用户基本操作

- 查看用户
  ```shell
  select user(); # 查看当前登陆的用户
  select user from mysql.user; # 显示数据库服务器中所有用户列表
  ```

- 用户创建、删除
  ```shell
  create user 'sec_user'@'localhost' identified by 'password'; # 创建用户
  drop user 'sec_user'@'localhost'; # 删除sec_user用户的命令
  ```

- 用户登陆
  创建完用户便可以使用下面的指令登陆了
  ```shell
  mysql -h host_name -P port -u user_name -p
  # 如下指令
  mysql -h localhost -P port -u sec_user -p # 提示输入密码即可
  ```

- 用户权限与授权
  查看对应用户指令的权限
  ```shell
  show grants for sec_user@localhost; # 查看用户权限
  ```

  对用户进行授权使用的是grant命令，格式如下
  ```shell
  grant <privilege_type> on <privilege_level> to sec_user@localhost;
  ```

  其中<privilege_type>为权限类别，<privilege_level>为权限层级，指明在什么数据库的什么表生效.如
  <br>
  ```shell
  # 将所有权限赋予上面创建的`sec_user`用户
  grant all privileges on demo.* to 'sec_user'@'localhost';
  ```

  刷新权限设置，使其立即生效
  ```shell
  flush privileges;
  ```

  撤销权限使用下面的指令
  ```shell
  revoke drop on demo.* from 'sec_user'@'localhost';
  ```

### 数据库数据操作

- 创建、删除数据库表
  ```shell
  create table person (
    name varchar(10),
    sex varchar(2),
    age int
    ); # 创建

  desc person; # 查看表的格式
  drop table person; # 删除
  ```
  其中，person为表名，表包括3列，name、sex、age

- 查看当前数据库的所有的表
  ```shell
  use <database>;
  show tables;
  ```

- 插入数据
  ```shell
  # 插入所有列
  insert into person values("zhangsan","nan",18);
  # 插入部分列
  insert into person (name,age) values("zhangsan",18);
  ```

- 查看数据
  ```shell
  --查看所有数据
  select * from person;
  --查看符合条件的数据
  select * from person where age = 18;
  --查看同时符合多个条件的数据
  select * from person where age = 18 and sex = 'nan';
  --查看部分列的数据
  select name,sex from person where age = 18;
  --别名的使用，注：as可以省略
  select name as "姓名",sex as "性别" from person where age = 18;
  ```

- 更新数据
  ```shell
  --更新所有数据
  update person set name='lisi';
  --更新符合条件的数据
  update person set name='lisi' where age=18;
  ```

- 删除数据
  ```shell
  --删除表中的所有数据
  delete from person;
  --删除符合条件的所有数据
  update person set name='lisi' where age=18;
  ```


**注意MySQL的命令中的分号不要忘记了.**



## cmake使用sql

使用前，确保安装了sql的开发包，见[安装](#mysql数据库安装)  

然后使用下面的命令找到sql的库文件与头文件

```shell
find /usr -name "mysql.h" 2>/dev/null
find /usr -name "libmysqlclient*" 2>/dev/null
```

使用模板如下

- 不具备可移植性的手动路径
  - 头文件使用
  ```py
  # 对于特定可执行文件的头文件添加
  target_include_directories(main PRIVATE ${LIBMYSQLCLIENT_INCLUDE_DIRS}) # 其中LIBMYSQLCLIENT_INCLUDE_DIRS是头文件所在目录

  # 全局include，不需要额外target_include_directories
  include_directories(${LIBMYSQLCLIENT_INCLUDE_DIRS})
  ```
  - 库文件使用
  法一，使用find_library() + target_link_libraries()
  ```py
  find_library(LIBMYSQLCLIENT
    NAMES mysqlclient
    PATHS /usr/lib/x86_64-linux-gnu /usr/local/lib # 这里是库文件可能存在的目录，如果知道具体的，填一个就行
  )

  target_link_libraries(main PRIVATE ${LIBMYSQLCLIENT})
  ```
  法二、直接指定库路径
  ```py
  # 直接链接动态库文件
  target_link_libraries(main PRIVATE /path/to/libmylib.so)

  # 或者指定库名和路径
  link_directories(/usr/local/lib /usr/lib/x86_64-linux-gnu) 
  # 直接包含整个库文件目录，不需要find_library()，相当于头文件的include_directories()了

  target_link_libraries(your_target_name mylib)
  ```

- 官网教程(可移植性)
  官网的教程虽然好，但是容易出现版本兼容问题，但是具有可移植性，自己找路径

  **通常是搭配find_package()使用**
  ```py
  # The minimum required version hasn't been tested. Feel free to adjust
  # downwards if necessary.
  cmake_minimum_required(VERSION 3.0)
  project(hello-mysql-world C)
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c99")
  
  include(FindPkgConfig)
  pkg_check_modules(LIBMYSQLCLIENT REQUIRED mysqlclient)
  
  foreach(FLAG ${LIBMYSQLCLIENT_CFLAGS_OTHER})
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${FLAG}")
  endforeach()
  
  link_directories(${LIBMYSQLCLIENT_LIBRARY_DIRS})
  
  add_executable(hello hello.c)
  target_include_directories(hello PRIVATE ${LIBMYSQLCLIENT_INCLUDE_DIRS})
  target_link_libraries(hello PRIVATE ${LIBMYSQLCLIENT_LIBRARIES})
  ```

## 参考

https://blog.csdn.net/weixin_45626288/article/details/133220238

https://blog.csdn.net/weixin_37926734/article/details/127464037

https://blog.csdn.net/fightingXia/article/details/82720973

https://github.com/jaywcjlove/mysql-tutorial