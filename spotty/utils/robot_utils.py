#                                                                               
# Copyright (c) 2025, FAU, Shukrullo Nazirjonov
# All rights reserved. Licensed under the MIT license.
# See LICENSE file in the project root for details.
#                                                                               
HOSTNAME = "192.168.80.3"   #"172.20.10.12"  # Hotspot IP
USERNAME = "adc"   #"user"
PASSWORD = "automation_ws2526"   #"PASSWORD"

def auto_authenticate(robot):
    robot.authenticate(USERNAME, PASSWORD, timeout=20)
    robot.sync_with_directory()
    robot.time_sync.wait_for_sync()
