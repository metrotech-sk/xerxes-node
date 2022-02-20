cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 20)

# set the project name
project(xerxes-master)


find_package(PkgConfig)
pkg_check_modules(SERIAL libserial)

include_directories("./include")

add_library(xerxes SHARED "stopwatch.cpp" "protocol.cpp" "rs485.cpp") 

target_link_libraries(xerxes ${SERIAL_LIBRARIES})


# add_executable(test "node-main.cpp")
# target_link_libraries(test xerxes)
