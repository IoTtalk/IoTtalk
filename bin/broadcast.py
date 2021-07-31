#!/usr/bin/env python3
import fcntl
import socket
import struct
import subprocess
import time

import ec_config



def get_ip_address(s, interface):
    '''
    :param s: the socket instance
    :param interface: e.g. eth0, wlan0.
    '''
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack(b'256s', interface[:15].encode())
    )[20:24])


if __name__ == '__main__':
    # check interface name
    if ec_config.AUTO_DETECT_BROADCAST_IF:
        result = subprocess.check_output(['sudo', 'cat', '/etc/NetworkManager/system-connections/EC-Hotspot'])
        for line in result.split():
            line = str(line, 'utf8')
            if line.startswith('interface-name'):
                interface_name = line.split('=')[1].strip()
                if interface_name != ec_config.BROADCAST_IF:
                    print('ec_config.BROADCAST_IF needs update: "{}" -> "{}"'.format(ec_config.BROADCAST_IF, interface_name))
                    ec_config.BROADCAST_IF = interface_name

    # init socket for broadcast
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    bind_ip = get_ip_address(skt, ec_config.BROADCAST_IF)
    skt.bind((bind_ip, 0))
    print('Bind socket on {} {}'.format(ec_config.BROADCAST_IF, bind_ip))

    skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        try:
            skt.sendto(b'easyconnect', ('<broadcast>', ec_config.BROADCAST_PORT))
        except OSError:     # Network is unreachable
            print('OSError', e)
            time.sleep(3)
            exit()

        time.sleep(1)

