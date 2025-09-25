cmake_minimum_required(VERSION 3.10.2)
set(CMAKE_CXX_STANDARD 14)

# 主项目名称
project(main_project)
# # 静态库生成的路径
# set(LIBPATH ${PROJECT_SOURCE_DIR}/lib)
# # 可执行程序的存储目录
# set(EXECPATH ${PROJECT_SOURCE_DIR}/bin)
# # 头文件目录
# set(HEADPATH ${PROJECT_SOURCE_DIR}/inc)

# # 库文件的名字
# set(HELLO hello)
# # set(SORTLIB sort)

# # 可执行程序的名字
# set(EXECNAME main)
# # set(EXECNAME2 main2)

# # 添加子节点目录
# # add_subdirectory(source_dir [binary_dir] [EXCLUDE_FROM_ALL])
MESSAGE("1")
add_subdirectory(src)
MESSAGE("2")
