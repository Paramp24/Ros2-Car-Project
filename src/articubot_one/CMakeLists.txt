cmake_minimum_required(VERSION 3.8)
project(articubot_one)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config description launch worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    src/obstacle_avoidance.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()