"""
This module contain information about the master node and its connector
"""
import urllib3
import json
import time
import socket
import struct


class StreamConnector(object):
    def __init__(self, server_addr, server_port, token="None", std_idle_time=0, max_try=9):
        # Check instance type
        if not isinstance(server_port, int):
            raise TypeError("Invalid port data type! Require int, but got others")

        # Check for server address
        if not (self.__is_valid_ipv4(server_addr) or self.__is_valid_ipv6(server_addr)):
            raise AttributeError("Invalid IP address!")

        # Check token type
        if not isinstance(token, str):
            raise TypeError("Invalid token data type! Require string, but got others")

        # Check max try type
        if not isinstance(max_try, int):
            raise TypeError("Invalid max_try type! Require int, but got others")

        self.__master_addr = server_addr
        self.__master_port = server_port
        self.__master_token = token
        self.__std_idle_time = std_idle_time
        self.__max_try = max_try

        # Connection string
        self.__str_master_status = "http://" + server_addr + ":" + str(server_port) + "/status?token=" + token
        self.__str_push_request = "http://" + server_addr + ":" + str(server_port) + "/streamRequest?token=" + token

        # URL Request
        self.__connector = urllib3.PoolManager()

    def is_master_alive(self):
        """
        Check for the master status that is it alive or not!
        :return: Boolean
        """
        try:
            response = self.__connector.request('GET', self.__str_master_status)

            if response.status == 200:
                return True
        except:
            return False

    def __get_stream_end_point(self):
        """
        Request for the stream end point from the master.
        :return: Boolean(False) when the system is busy.
                 Tuple(batch_addr, batch_port, tuple_id) if the batch or messaging system is available.
        """
        response = self.__connector.request('GET', self.__str_push_request)

        if response.status == 406:
            # Messages in queue is full. Result in queue lock.
            print("Queue in master is full.")
            return False
        elif response.status != 200:
            return False

        try:
            content = json.loads(response.data.decode('utf-8'))

            return (content['c_addr'], int(content['c_port']), int(content['t_id']), )

        except:
            print("JSON content error from the master!\n" + response.data.decode('utf-8'))
            return False

    def __push_stream_end_point(self, target, data):
        """
        Create a client socket to connect to server
        :param target: Tuple with three parameter from the endpoint request
        :param data: ByteArray which holds the content to be streamed to the batch.
        :return: Boolean return status
        """

        s = None
        for res in socket.getaddrinfo(target[0], target[1], socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except OSError as msg:
                s = None
                continue
            try:
                s.connect(sa)
            except OSError as msg:
                s.close()
                s = None
                continue
            break
        if s is None:
            print('could not open socket')
            print("Cannot connect to " + target[0] + ":" + str(target[1]))
            return False

        with s:
            # Identifying object id
            s.sendall(data)
            s.sendall(b'')
            s.close()

        return True

    def send_data(self, data):
        # The data must be byte array
        if not isinstance(data, bytearray):
            raise TypeError("Invalid data type! Require ByteArray, but got others")

        if len(data) == 0:
            print("No content in byte array.")
            return None

        c_target = self.__get_stream_end_point()
        counter = self.__max_try
        while not c_target:
            time.sleep(self.__std_idle_time)
            c_target = self.__get_stream_end_point()
            counter -= 1
            if counter == 0:
                print("Cannot contact server. Exceed maximum retry {0}.".format(self.__max_try))
                return False

        counter = self.__max_try
        while not self.__push_stream_end_point(c_target, data):
            time.sleep(self.__std_idle_time)
            counter -= 1
            if counter == 0:
                print("Cannot contact server. Exceed maximum retry {0}.".format(self.__max_try))
                return False

        print("Send data to " + c_target[0] + ":" + str(c_target[1]) + " successful.")

    def get_data_contaner(self):
        return bytearray(8)

    def __is_valid_ipv4(self, ip):
        import re
        pattern = re.compile(r"""
            ^
            (?:
              # Dotted variants:
              (?:
                # Decimal 1-255 (no leading 0's)
                [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
              |
                0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
              |
                0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
              )
              (?:                  # Repeat 0-3 times, separated by a dot
                \.
                (?:
                  [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
                |
                  0x0*[0-9a-f]{1,2}
                |
                  0+[1-3]?[0-7]{0,2}
                )
              ){0,3}
            |
              0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
            |
              0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
            |
              # Decimal notation, 1-4294967295:
              429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
              42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
              4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
            )
            $
        """, re.VERBOSE | re.IGNORECASE)
        return pattern.match(ip) is not None


    def __is_valid_ipv6(self, ip):
        import re
        pattern = re.compile(r"""
            ^
            \s*                         # Leading whitespace
            (?!.*::.*::)                # Only a single whildcard allowed
            (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
            (?:                         # Repeat 6 times:
                [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
                (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            ){6}                        #
            (?:                         # Either
                [0-9a-f]{0,4}           #   Another group
                (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
                [0-9a-f]{0,4}           #   Last group
                (?: (?<=::)             #   Colon iff preceeded by exacly one colon
                 |  (?<!:)              #
                 |  (?<=:) (?<!::) :    #
                 )                      # OR
             |                          #   A v4 address with NO leading zeros
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                (?: \.
                    (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                ){3}
            )
            \s*                         # Trailing whitespace
            $
        """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
        return pattern.match(ip) is not None
