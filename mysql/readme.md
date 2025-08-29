# mysql数据库

## 背景

想开发一台高性能web服务器，发现数据库这部分的知识空白，便学习一下

## 目录

[安装](#mysql数据库安装)  
[基本使用](#mysql数据库基本使用)  

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

## mysql数据库基本使用

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



## 参考

https://blog.csdn.net/weixin_45626288/article/details/133220238

https://blog.csdn.net/weixin_37926734/article/details/127464037

https://blog.csdn.net/fightingXia/article/details/82720973
