from channels.asgi import get_channel_layer

import strut

strut.setup()


channel_layer = get_channel_layer()
