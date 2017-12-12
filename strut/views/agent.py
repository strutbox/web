from time import time
from django.http import JsonResponse
from django.views import View


class Ping(View):
    def get(self, request):
        return JsonResponse({'time': int(time()*1000)})
