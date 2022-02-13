cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 20)

# set the project name
project(xerxes-master)

find_package(PkgConfig)
pkg_check_modules(SERIAL libserial)

add_library(${PROJECT_NAME}_bus INTERFACE)

target_include_directories(${PROJECT_NAME}_bus INTERFACE include)


add_library(${PROJECT_NAME}_serial
        src/rs485.cpp)

target_include_directories(${PROJECT_NAME}_serial
        PUBLIC
        include
        PRIVATE
        ${SERIAL_INCLUDE_DIRS})

target_link_libraries(${PROJECT_NAME}_serial
        PUBLIC ${PROJECT_NAME}_bus
        PRIVATE ${SERIAL_LDFLAGS})
#
## add the executable
#add_executable(test test.cpp)
#target_link_libraries(test xerxes)
