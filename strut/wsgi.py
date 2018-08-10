from django.core.wsgi import get_wsgi_application
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry

import strut

strut.setup()

application = Sentry(get_wsgi_application())
