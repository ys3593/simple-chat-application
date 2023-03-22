import sys
from server import Server
from client import Client


def isIPv4(s):
    try:
        return str(int(s)) == s and 0 <= int(s) <= 255
    except:
        return False


def isIPv6(s):
    if len(s) > 4:
        return False
    try:
        return int(s, 16) >= 0 and s[0] != '-'
    except:
        return False


if __name__ == '__main__':
    mode = sys.argv[1]

    # initiates the server process
    if mode == '-s':
        # check error before passing
        if len(sys.argv) != 3:
            sys.exit(">>> [Please pass server port to initiate the server process.]")

        # try:
        #     port = int(sys.argv[2])
        #     # 1024 - 65535 are available
        #     if port < 1024 or port > 65535:
        #         sys.exit(">>> [Server port should be between 1024 - 65535.]")
        # except:
        #     sys.exit(">>> [Server port should be int.]")

        Server(int(sys.argv[2]))

    # initiates client communication to the serve
    elif mode == '-c':
        # check error before passing
        if len(sys.argv) != 6:
            sys.exit(">>> [Please pass user name, server ip, server port and client port to client the server process.]")

        user_name = sys.argv[2]

        # if  sys.argv[3] == "localhost":
        #     pass
        # elif sys.argv[3].count(".") == 3 and all(isIPv4(i) for i in sys.argv[3].split(".")):
        #     pass
        # elif sys.argv[3].count(":") == 7 and all(isIPv6(i) for i in sys.argv[3].split(":")):
        #     pass
        # else:
        #     sys.exit(">>> [Invalid ip address.]")

        # try:
        #     port = int(sys.argv[4])
        #     # 1024 - 65535 are available
        #     if port < 1024 or port > 65535:
        #         sys.exit(">>> [Server port should be between 1024 - 65535.]")
        # except:
        #     sys.exit(">>> [Server port should be int.]")

        # try:
        #     port = int(sys.argv[5])
        #     # 1024 - 65535 are available
        #     if port < 1024 or port > 65535:
        #         sys.exit(">>> [Client port should be between 1024 - 65535.]")
        # except:
        #     sys.exit(">>> [Client port should be int]")

        server_ip = sys.argv[3]
        server_port = int(sys.argv[4])
        client_port = int(sys.argv[5])
        Client(user_name, server_ip, server_port, client_port)

    else:
        sys.exit(">>> [Please use -s to initiate the server process or -c to initiate the client process.]")
