# test_graph_nav_run.py
from spotty.mapping.graph_nav_interface import GraphNavInterface
import bosdyn.client
from spotty.utils.robot_utils import HOSTNAME, auto_authenticate

sdk = bosdyn.client.create_standard_sdk("GraphNavTest")
robot = sdk.create_robot(HOSTNAME)
auto_authenticate(robot)

gi = GraphNavInterface(robot, 'assets/maps/Map1')  # or your map path
gi.run()