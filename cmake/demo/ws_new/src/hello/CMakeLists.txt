cmake_minimum_required(VERSION 3.10.2)
project(hello)

# 搜索源文件
aux_source_directory(./src src_list)
# 添加头文件
include_directories(${HEADPATH})
# 设置库文件存储的位置
set(LIBRARY_OUTPUT_PATH ${LIBPATH})
# 制作静态库文件
add_library(${HELLO} STATIC ${src_list})

MESSAGE("hello")
