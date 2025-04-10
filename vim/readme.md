### vim配置与技巧

#### vim配置文件

- 查看vim配置文件出现的位置
    ```shell
    vim --verison
    ```
    其中包含以下信息
    ```txt
    system vimrc file:      "$VIM/vimrc"
    user vimrc file:        "$HOME/.vimrc"
    2nd user vimrc file:    "~/.vim/vimrc"
    user exrc file:         "$HOME/.exrc"
    system gvimrc file:     "$VIM/gvimrc"
    user gvimrc file:       "$HOME/.gvimrc"
    2nd user gvimrc file:   "~/.vim/gvimrc"
    defaults file:          "$VIMRUNTIME/defaults.vim"
    system menu file:       "$VIMRUNTIME/menu.vim"
    fall-back for $VIM:     "/usr/share/vim"
    ```
    而我们的个人用户的vim配置路径一般在<strong>~/.vimrc</strong>
    <br>

- 我的常用配置文件
    ```vim
    " show the lines
    set nu

    " 设置鼠标模式，=a即all,任何状态都能用
    set mouse=a

    " set the tab
    set ts=4
    set shiftwidth=4

    " incremental search
    set is

    " smartindex
    set smartindent

    " show cmd
    set showcmd

    " symbol match
    autocmd FileType python,javascript,cpp,c inoremap   { {}<Left>
    autocmd FileType python,javascript,cpp,c inoremap   ( ()<Left>
    " autocmd FileType python,javascript,cpp,c  inoremap < <><Left>
    autocmd FileType python,javascript,cpp,c inoremap   [ []<Left>
    autocmd FileType python,javascript,cpp,c inoremap   " ""<Left>
    autocmd FileType python,javascript,cpp,c inoremap   ' ''<Left>
    ```

#### vim使用技巧

- visual模式下将内容复制到系统粘贴板
  **查看是否可以使用系统粘贴板**
    ```shell
    vim --version | grep clipboard
    ```
    如果出现 "+clipboard"即可使用，否则可以重新安装vim.<br>
    <br>

    **直接使用**
    ```shell
    normal模式下，执行命令：gg #光标移动到开头
    v 进入visual模式，G即可选中全部，按y复制到vim粘贴板，按"+y复制到系统粘贴板.
    ```

    <br>
    当然也可以选中指定的行间的块，用以下命令

    ```shell
    normal模式下 执行命令:<line_num1>G
    进入visual模式，执行命令：<line_num2>G,按下y或者"+y即可
    ```

    <br>

    **修改vim的快捷键**

    ~~建议不要修改~~

    修改系统的快捷键可能会导致部分命令冲突，需谨慎.

    下面可以往配置文件里加入以下修改项

    ```vim
    vnoremap <C-c> "+y
    ```

    <br>

- 从系统粘贴板复制到vim
    执行以下指令即可

    ```shell
    "+p
    或者<crtl+shift+v> #我的ubuntu可以
    ```

- vim 批量替换字符串
  - 全局替换
    ```vim
    :%s/word1/word2/g
    ```
    如果是转义字符，需要加\。例如，全局将'\'替换为'/'，使用以下命令
    ```vim
    :%s/\\/\//g
    ```
  - 部分替换
    ```vim
    n1,n2s/word1/word2/g
    ```

- 推荐一篇文章
    https://www.cnblogs.com/gmpy/p/11177719.html

#### 后话

vim的内容还有很多，后续会更新.



    