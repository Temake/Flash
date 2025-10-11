

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from chats.routers import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_asgi_application()


routers =[
    {"http": get_asgi_application(),
     "websocket": ProtocolTypeRouter(URLRouter(websocket_urlpatterns))}
]