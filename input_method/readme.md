# 浅谈输入法

## 目录

[前置知识](#前置知识)  
[查看系统字体](#查看系统已安装字体)  
[安装字体](#安装字体)  

## 前置知识

输入法包括：
- **输入法框架**，即ibus、fcitx、fcitx5之类的.
    <br>
    上面这一大类在系统中叫做<strong>keyboard input method system</strong>，如下图所示.

    ![input method system](images/a.png)

    <br>
- **输入法引擎**，即fcitx5下的pinyin、rime之类的.
    <br>
    这一类就真的是<strong>input method</strong>,如下图所示.

    ![input method](images/b.png)

    上图为fcitx5框架下的input-method-config界面.

- **词库**

## 查看系统已安装字体

- 查看全部字体(保护系统和用户个人的)
  ```shell
  fc-list
  ```

- 查看支持中文的字体
  ```shell
  fc-list :lang=zh
  ```

  也可以排序查看

  ```shell
  fc-list :lang=zh | sort
  ```

  下面这种也行
  ```shell
  fc-list | grep CN
  ```

## 安装字体

### 安装到系统

查看系统中安装的字体
```shell
fc-list
```

如果我们想把我们的字体安装到系统，执行下面的操作

- 创建个人字体目录
  ```shell
  cd /usr/share/fonts
  sudo mkdir my_fonts
  ```

- 复制安装的字体(通常为.ttf格式等)
  ```shell
  sudo mv ~/Downloads/fonts/xxx.ttf /usr/share/fonts/  my_fonts
  ```

- 安装到系统
  ```shell
  sudo mkfontscale
  sudo mkfontdir
  sudo fc-cache
  ```

- 如果想删除字体，直接执行下面的指令
  ```shell
  sudo rm -rf /usr/share/fonts/my_fonts
  ```

参考：https://zhuanlan.zhihu.com/p/463400886

### 安装到个人用户

原理与安装到系统类似，改一下目录即可

- 创建用户字体目录(如果没有)
  ```shell
  cd ~/.local/share
  mkdir fonts
  ```

- 创建个人字体
  ```shell
  mkdir my_fonts
  cd my_fonts
  cp <fonts_dir>/*.ttf .
  ```

- 安装
  ```shell
  mkfontscale
  mkfontdir
  fc-cache
  ```