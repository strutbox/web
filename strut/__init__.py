def setup(settings="strut.settings"):
    import os

    os.environ["DJANGO_SETTINGS_MODULE"] = settings

    import django

    django.setup()
