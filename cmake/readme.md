# cmake的配置及使用

<br>

## 目录

[背景](#背景)  
[安装](#cmake安装)  
[cmake模板](#cmake常用模板)  
[cmake嵌套](#cmake嵌套)  
[其他cmake技巧](#cmake技巧)  

<br>  

## 背景

由于cmake的简单用法比较简单，且零基础的网上的教学更好，在这里我直接放一个常用模板和其他技巧性的功能.

可参考我在gitee上的学习过程： https://gitee.com/cuijunjie18/cmake-learning  

<br>

## cmake安装

直接执行下面的指令即可
```shell
sudo apt-get install cmake
```

<br>

## cmake常用模板

一、新手向的模板

参考url：https://gitee.com/cuijunjie18/cmake-learning

```cmake
cmake_minimum_required(VERSION 3.10)

project(Test)

aux_source_directory(${PROJECT_SOURCE_DIR}/main_src SRC)

# 设置可执行文件的生成位置
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

#[[
MESSAGE("This is BINARY dir ${PROJECT_BINARY_DIR}")
MESSAGE("This is SOURCE dir ${PROJECT_SOURCE_DIR}")
MESSAGE("This is INSTALL dir ${CMAKE_INSTALL_PREFIX}") # 默认/usr/local
]]

# 查找库文件hello(默认)
find_library(HELLO hello ${PROJECT_SOURCE_DIR}/lib_src)

# 判断库是否找到
IF(NOT HELLO)
    MESSAGE("HELLO not found")
ENDIF(NOT HELLO)

MESSAGE("This is dir of lib ${HELLO}")

# 导入头文件
include_directories(${PROJECT_SOURCE_DIR}/install/${PROJECT_NAME}/include)

add_executable(a.x ${SRC})

# target_link_libraries(a.x ${PROJECT_SOURCE_DIR}/lib_src/libhello.so)
target_link_libraries(a.x ${HELLO})

# 更改默认安装位置
set(CMAKE_INSTALL_PREFIX ${PROJECT_SOURCE_DIR}/install)

# 要执行make install才行(问题是这样安装a.x无法成功连接库)
# install(TARGETS
#     a.x
#     DESTINATION ${PROJECT_NAME}/bin
# )

# 安装已有文件
install(FILES
    bin/a.x
    DESTINATION ${PROJECT_NAME}/bin
)
```

二、ros2的模板

参考url：https://github.com/cuijunjie18/semantic_segmentation-mine/blob/master/engineer_detector/CMakeLists.txt

```cmake
# 为clangd产生配置文件
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# O3优化
add_compile_options(-O3)

cmake_minimum_required(VERSION 3.10)

project(engineer_detector)

# 从bash脚本中读入变量
set (EXE "$ENV{EXE}" CACHE STRING "EXE passed from temp env variable") 

if (NOT EXE)
    set (EXE "main" CACHE STRING "dafault name" FORCE)
endif()

# message("EXE is ${EXE}")

# 查找包
find_package(OpenCV REQUIRED)
find_package(OpenVINO REQUIRED)
find_package(rclcpp REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)

# 头文件
include_directories(${PROJECT_SOURCE_DIR}/include)

# # 导入目标源码
# aux_source_directory(detector_node.cpp engineer_detector.cpp SRC) # PROJECT_BINARY_DIR为执行cmake命令的位置

# 设置可执行文件生成路径
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

# 1，分割节点
add_executable(
	${EXE} 
	src/main.cpp
	src/detector_node.cpp 
	src/engineer_detector.cpp	
)

# ros2的库链接方法
ament_target_dependencies(
  ${EXE}
  "rclcpp"
  "std_msgs"
  "sensor_msgs"
  "cv_bridge"
)

target_link_libraries(
    ${EXE}
    ${OpenCV_LIBS}
    openvino::runtime
)

# 2，测试部分：生成一个模拟相机
add_executable(test_as_pb ${PROJECT_SOURCE_DIR}/src/test_as_pb.cpp)
ament_target_dependencies(
  test_as_pb 
  "rclcpp"
  "std_msgs" 
  "sensor_msgs"
  "cv_bridge"
)

target_link_libraries(
    test_as_pb 
	${OpenCV_LIBS} 
	openvino::runtime
)
```

三、库编译、安装模版

```cmake
cmake_minimum_required(VERSION 3.8)

project(Test)

# 已经搜索了目录下的所有源文件，不能再${INC}/hello.hpp,因为已经包含了
aux_source_directory(${PROJECT_SOURCE_DIR}/src SRC) # 源码路径(待生成库的源文件)
aux_source_directory(${PROJECT_SOURCE_DIR}/include INC) # 头文件路径

MESSAGE("This is the source_dir ${PROJECT_SOURCE_DIR}")

# 添加头文件路径(如果不加，默认不清楚)
# 添加了头文路径件才能正确生成库(库源码里导入了头文件)，才能正确安装
include_directories(${PROJECT_SOURCE_DIR}/include)

# 添加要生成的库
add_library(hello_static STATIC ${SRC})
add_library(hello_shared SHARED ${SRC})

# 设置库的名称
set_target_properties(hello_static PROPERTIES OUTPUT_NAME "hello") # 静态,实际生成的名称为libhello.a
set_target_properties(hello_shared PROPERTIES OUTPUT_NAME "hello") # 动态，libhello.so

# 设置库的生成位置
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR})

# 更改默认安装位置
set(CMAKE_INSTALL_PREFIX ${PROJECT_SOURCE_DIR}/../install)

# 安装库
install(TARGETS
    hello_static hello_shared
    LIBRARY DESTINATION ${PROJECT_NAME}/lib
    ARCHIVE DESTINATION ${PROJECT_NAME}/lib
)

# 安装头文件
install(FILES
    include/hello.hpp
    DESTINATION ${PROJECT_NAME}/include
)
```

<br>

## cmake嵌套

为什么需要CMakeLists.txt文件嵌套呢？因为当项目结构、功能过多的时候，如果只用一个CMakeLists.txt的话逻辑就会过长.

简单参考： https://blog.csdn.net/weixin_43808717/article/details/138403467

**核心操作add_subdirectory()**

我的理解：当执行到add_subdirectory时，就会进入对应的CMakeLists.txt中进行cmake操作，所以一般使用cmake变量**CMAKE_CURRENT_SOURCE_DIR**

具体简单例子可见：[demo嵌套](demo/ws_new)  

<br>

## cmake技巧

- 设置c++标准
  
    ```cmake
    # 设置 C++ 标准
    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    ```

- 设置变量

    ```cmake
    set (Variable_name value)
    ```

- 从环境导入变量

    ```cmake
    # 从bash脚本中读入变量
    set (EXE "$ENV{EXE}" CACHE STRING "EXE passed from temp env variable") 

    if (NOT EXE)
        set (EXE "main" CACHE STRING "dafault name" FORCE)
    endif()
    ```
    **注意这里的CACHE STRING,如果使用过一个环境变量设置cmake变量，那么默认下一次从cache中读取，哪怕环境变量变了**(这是cmake build的一个恶心之处)，可以使用下面两种方式解决.

    (1)在bash脚本中手动删除cache
    ```shell
    rm -rf build
    ```
    但是这样删除了一些快速编译的cache,会导致编译速度变慢.

    (2)cmake中设置FORCE参数
    ```cmake
    # 从bash脚本中读入变量
    set (EXE "$ENV{EXE}" CACHE STRING "EXE passed from temp env variable" FORCE)  #设置FORCE参数，强制覆盖cache变量

    if (NOT EXE)
        set (EXE "main" CACHE STRING "dafault name" FORCE)
    endif()
    ```

- 输出调试信息，使用message
  ```cmake
  # 不同样式的信息
  message(STATUS "var = ${VAR}")
  message(WARNING "var = ${VAR}")
  message(AUTHOR_WARNING "var = ${VAR}")
  message(FATAL_ERROR "var = ${VAR}") # 中断执行
  ```

- 头文件、库的查找、使用
  可以[sql的cmake使用](../mysql/readme.md)为具体案例学习

- 添加全部源文件
  ```cmake
  # 法一
  file(GLOB http_src ${SRC_DIR}/http/*.cpp)

  # 法二
  aux_source_directory(${SRC_DIR}/http http_src)
  ```

- install的使用
  ```cmake
  # 安装由cmake过程中生成的文件，即target，会根据目标的类型自动识别到对应的路径
  install(TARGETS <A> <B> <C> <D>
        LIBRARY DESTINATION <path_1>    # 动态库
        ARCHIVE DESTINATION <path_2>    # 静态库
        INCLUDES DESTINATION <path_3>   # 头文件
        RUNTIME DESTINATION <path_4>    # 可执行文件
  )

  install(FILES <file_a_path>
        DESTINATION <install_path>  # 直接指定路径
  )
  ```

  安装的时候再进入build目录执行下面指令即可
  ```shell
  make install
  ```

  注意：安装路径可能不是全局的，是相对的，比如在项目根目录下设置的相对路径，进入build下安装则相对build目录而言了，下面有个例子
  ```cmake
  cmake_minimum_required(VERSION 3.10)
  project(Demo)
  
  SET(CMAKE_CXX_STANDARD 17)
  SET(CMAKE_CXX_STANDARD_REQUIRED ON)
  set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
  
  include_directories(${CMAKE_CURRENT_SOURCE_DIR})
  
  add_library(
      my_math
      SHARED
      ${CMAKE_CURRENT_SOURCE_DIR}/my_math.cpp   # 这里是相对当前的cmake，但是安装后是相对build了
  )
  
  add_executable(
      demo
      ${CMAKE_CURRENT_SOURCE_DIR}/demo.cpp
  )
  
  install(TARGETS my_math
      LIBRARY DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/lib
  )
  
  install(FILES
      ${CMAKE_CURRENT_SOURCE_DIR}/my_math.h
      DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/include
  )
  
  install(TARGETS demo
      RUNTIME DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/bin
  )
  ```


<br>

## 后记

作者寄语：当cmake调试一直有问题，直接删除build、cache,这可能会解决问题.(血与泪的经验)