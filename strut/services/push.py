import sys


def build_endpoint_description_string(bind):
    if bind.ipv4:
        return f"tcp:port={bind.ipv4[1]}:interface={bind.ipv4[0]}"
    if bind.unix:
        return f"unix:{bind.unix}:mode=777"
    return f"fd:fileno={bind.fd}"


class Service:
    def __init__(self, bind):
        self.bind = bind

    def start(self):
        import strut

        strut.setup()

        from django.conf import settings
        from channels import DEFAULT_CHANNEL_LAYER
        from channels.layers import get_channel_layer
        from channels.routing import get_default_application
        from daphne.access import AccessLogGenerator
        from daphne.server import Server

        application = get_default_application()
        channel_layer = get_channel_layer(DEFAULT_CHANNEL_LAYER)

        endpoint = build_endpoint_description_string(self.bind)

        print(f"> listening on {endpoint}...")
        Server(
            application=application,
            signal_handlers=True,
            # channel_layer=channel_layer,
            endpoints=[endpoint],
            # ws_protocols=getattr(settings, "CHANNELS_WS_PROTOCOLS", None),
            action_logger=AccessLogGenerator(sys.stdout),
            ping_interval=20,
            ping_timeout=30,
            websocket_timeout=-1,  # forever
            websocket_handshake_timeout=5,
            verbosity=1,
            proxy_forwarded_address_header="X-Forwarded-For",
            proxy_forwarded_port_header="X-Forwarded-Port",
            # proxy_forwarded_proto_header="X-Forwarded-Proto",
        ).run()
