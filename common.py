from collections import namedtuple, ChainMap
from functools import wraps

Group = namedtuple("Group", [
    "clients",
    "id",
    "muted",
    "name",
    "stream_id",
])

Server = namedtuple("Server", [
    "groups",
])

Client = namedtuple("Client", [
    "config",
    "connected",
    "id",
])

Config = namedtuple("Config", [
    "volume"
])

Volume = namedtuple("Volume", [
    "muted",
    "percent",
])

def incrementing_id(func):
    id = 1
    @wraps(func)
    def wrapper(*args, **kwds):
        nonlocal id
        result = func(id, *args, **kwds)
        id += 1
        return result
    return wrapper

@incrementing_id
def doRequest(requestId, client, method, params=None):
    from json import dumps, loads
    request = {'method': method, 'jsonrpc': '2.0', 'id': requestId}
    if params:
        request.update({'params': params})
    print("send: " + dumps(request))
    client.write((dumps(request) + "\r\n").encode('ascii'))
    while (True):
        response = client.read_until("\r\n".encode('ascii'), 2)
        jResponse = loads(response.decode())
        if 'id' in jResponse:
            if jResponse['id'] == requestId:
                if 'result' in jResponse:
                    return jResponse['result']
                elif 'error' in jResponse:
                    raise Exception(jResponse['error'])
    return

def mute_groups_by_stream(client, stream, mute_mode):
    res = doRequest(client, 'Server.GetStatus')
    groups_to_unmute = (group for group in res['server']['groups'] if group["stream_id"] == stream and not group["muted"] == mute_mode)
    for group in groups_to_unmute:
        doRequest(client, 'Group.SetMute', {"id": group["id"], "mute": mute_mode})

def parsedargs(description):
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--server', type=str, default="127.0.0.1")
    parser.add_argument('--port', type=int, default=1705)
    parser.add_argument('stream', type=str)
    return parser.parse_args()
