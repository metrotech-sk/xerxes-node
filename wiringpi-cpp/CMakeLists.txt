cmake_minimum_required(VERSION 3.10)

# set the project name
project(xerxes-master)

# add the executable
add_executable(test test.cpp)

find_library(WIRINGPI_LIBRARIES NAMES wiringPi)
target_link_libraries(test ${WIRINGPI_LIBRARIES})