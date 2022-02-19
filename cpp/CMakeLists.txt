cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 20)

# set the project name
project(xerxes-master)

find_package(XeusProtocol REQUIRED)
find_package(SerialBus REQUIRED)

add_executable(test node-main.cpp)
target_link_libraries(test SerialBus::SerialBus XeusProtocol::XeusProtocol)
