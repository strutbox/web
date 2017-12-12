from django.urls import path, include

from .views import agent

urlpatterns = [
    path('api/0/', include([
        path('agent/', include([
            path('ping/', agent.Ping.as_view()),
        ])),
    ])),
]
