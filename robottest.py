from bosdyn.client import create_standard_sdk
from bosdyn.client.robot_state import RobotStateClient
from bosdyn.client.estop import EstopClient
from bosdyn.client.power import PowerClient
from bosdyn.client.lease import LeaseClient
from bosdyn.client.util import authenticate

ROBOT_IP = "192.168.80.3"  # change if needed

def main():
    sdk = create_standard_sdk("spot-status-check")
    robot = sdk.create_robot(ROBOT_IP)
    authenticate(robot)

    robot.sync_with_directory()
    robot.time_sync.wait_for_sync()

    print("\n=== BASIC ROBOT STATUS ===")

    # Robot state
    state_client = robot.ensure_client(RobotStateClient.default_service_name)
    state = state_client.get_robot_state()

    print(f"Power state: {state.power_state.motor_power_state}")
    print(f"Battery: {state.battery_states[0].charge_percentage.value:.1f}%")

    # Faults
    faults = state.system_fault_state.faults

    if not faults:
        print("No active faults")
    else:
        for fault in faults:
            print(f"- {fault.name}: {fault.error_message}")


    # E-Stop
    print("\n=== E-STOP STATUS ===")
    estop_client = robot.ensure_client(EstopClient.default_service_name)
    estop_status = estop_client.get_status()

    for endpoint in estop_status.endpoints:
        print(
            f"- {endpoint.name}: "
            f"{'STOPPED' if endpoint.stop_level else 'OK'}"
        )

    # Lease
    print("\n=== LEASE STATUS ===")
    lease_client = robot.ensure_client(LeaseClient.default_service_name)
    lease_state = lease_client.list_leases()

    if not lease_state.resources:
        print("No active leases")
    else:
        for resource in lease_state.resources:
            print(f"- Resource: {resource.resource}, Owner: {resource.lease_owner.client_name}")

    # Power capability
    print("\n=== POWER COMMAND CHECK ===")
    power_client = robot.ensure_client(PowerClient.default_service_name)
    print("Power command available:", power_client)

    print("\n=== STATUS CHECK COMPLETE ===")

if __name__ == "__main__":
    main()
