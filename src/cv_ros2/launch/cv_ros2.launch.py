import launch
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    pub_node=Node(
        package='cv_ros2',
        executable='pub_node',
    )
    sub_node=Node(
        package='cv_ros2',
        executable='sub_node',
    )

    nodes=[pub_node,sub_node]
    launch_d=LaunchDescription(nodes)
    return launch_d