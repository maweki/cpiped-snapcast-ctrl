#!/usr/bin/env python3
import telnetlib
from common import doRequest, mute_groups_by_stream, parsedargs
from itertools import chain, tee
from time import sleep

def main(connection, stream):
    res = doRequest(connection, 'Server.GetStatus')
    clients_of_stream = chain.from_iterable(group['clients'] for group in res['server']['groups'] if group["stream_id"] == stream)

    unmuted_clients = (client for client in clients_of_stream if not client['config']['volume']['muted'])
    clients_to_mute, clients_to_unmute = tee(unmuted_clients)

    for client in clients_to_mute:
        doRequest(connection, 'Client.SetVolume', params={
            "id": client["id"],
            "volume": { "percent": client['config']['volume']['percent'],
                        "muted": True}
        })

    sleep(0.2)

    mute_groups_by_stream(connection, stream, False)

    for client in clients_to_unmute:
        sleep(0.2)
        doRequest(connection, 'Client.SetVolume', params={
            "id": client["id"],
            "volume": { "percent": client['config']['volume']['percent'],
                        "muted": False}
        })


if __name__ == '__main__':
    args = parsedargs('snapcast stream mute')
    try:
        telnet = telnetlib.Telnet(args.server, args.port)
        main(telnet, args.stream)
    finally:
        telnet.close
