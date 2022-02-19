cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 20)

# set the project name
project(xerxes-master)

find_package(XeusProtocol REQUIRED)
find_package(SerialBus REQUIRED)

#include_directories("./include")
#
#add_library(xerxes SHARED "src/vectorop.cpp" "src/stopwatch.cpp" "src/protocol.cpp" "src/rs485.cpp" "src/p_leaf.cpp" "src/gpio_pin.cpp")
#
#target_link_libraries(xerxes ${SERIAL_LIBRARIES})


add_executable(test node-main.cpp)
target_link_libraries(test SerialBus::SerialBus XeusProtocol::XeusProtocol)
