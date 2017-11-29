#!/usr/bin/env python3
import telnetlib
from common import mute_groups_by_stream, parsedargs

def main(connection, stream):
    mute_groups_by_stream(connection, stream, True)

if __name__ == '__main__':
    args = parsedargs('snapcast stream mute')
    telnet = telnetlib.Telnet(args.server, args.port)
    main(telnet, args.stream)
    telnet.close
