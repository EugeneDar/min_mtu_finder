import subprocess
import sys
import socket
import re
import platform


def validate_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
        return True
    except socket.error:
        pass

    try:
        socket.inet_pton(socket.AF_INET6, address)
        return True
    except socket.error:
        pass

    if len(address) > 255:
        return False
    if address[-1] == '.':
        address = address[:-1]
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in address.split("."))


# def ping(address, data_size):
#     result = subprocess.run(
#         ["ping", "-4", "-M", "do", "-s", str(data_size), "-c", "1", "-n", address],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )
#     return str(result.stdout), str(result.stderr), result.returncode


def is_host_up(address):
    try:
        if platform.system().lower() == 'windows':
            command = ['ping', '-n', '1', address]
        else:
            command = ["ping", "-c", "1", address]
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


def find_minimal_mtu(destination):
    curr_mtu = 10000

    while curr_mtu >= 0:
        if platform.system().lower() == 'windows':
            command = ['ping', '-n', '1', '-f', '-l', str(curr_mtu - 28), destination]
        else:
            command = ['ping', '-4', '-n', '-c', '1', '-M', 'do', '-s', str(curr_mtu - 28), destination]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            break
        elif "message too long" in result.stderr:
            curr_mtu = int(re.findall(r'\d+', str(result.stderr))[0])
        else:
            raise Exception("ICMP requests may be blocked.")

    return curr_mtu


# def find_minimal_mtu(address):
#     headers_size = 28
#
#     min_mtu = headers_size
#     max_mtu = 50000
#
#     while min_mtu < max_mtu:
#         mid_mtu = (min_mtu + max_mtu + 1) // 2
#         try:
#             stdout, stderr, return_code = ping(address, mid_mtu - headers_size)
#             if return_code == 0:
#                 print(f'MTU {mid_mtu} OK', flush=True)
#                 min_mtu = mid_mtu
#             else:
#                 print(f'MTU {mid_mtu} TOO BIG', flush=True)
#                 max_mtu = mid_mtu - 1
#         except Exception as e:
#             raise Exception(f"An unexpected error occurred: {e}")
#
#     return min_mtu


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <destination_address>")
        sys.exit(1)

    destination_address = sys.argv[1]

    if not validate_address(destination_address):
        print(f"Host {destination_address} is bad format")
        sys.exit(1)

    if not is_host_up(destination_address):
        print(f"Host {destination_address} is not reachable")
        sys.exit(1)

    try:
        mtu = find_minimal_mtu(destination_address)
        print(f"Minimum MTU to {destination_address} is {mtu}")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
