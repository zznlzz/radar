#! /bin/zsh
source ~/.zshrc
sleep 10
roslaunch livox_ros_driver livox_lidar.launch publish_freq:=60
# sleep 5
# cd /home/pheonix/NewDisk/about_radar/Radar_structure/single_version/
# python main.py