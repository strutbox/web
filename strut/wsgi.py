from django.core.wsgi import get_wsgi_application

import strut

strut.setup()


application = get_wsgi_application()
