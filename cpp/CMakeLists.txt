cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 20)

# set the project name
project(xerxes-master)

include_directories("./include")

find_library(WIRINGPI_LIBRARIES NAMES wiringPi)

add_library(xerxes SHARED "src/VectorOp.cpp" "src/Stopwatch.cpp" "src/Protocol.cpp" "src/RS485.cpp" "src/Bus.cpp") 
target_link_libraries(xerxes ${WIRINGPI_LIBRARIES} )


# add the executable
add_executable(test test.cpp)
target_link_libraries(test xerxes)
