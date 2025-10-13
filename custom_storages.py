from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = getattr(
            settings, 'STATICFILES_LOCATION', 'static'
            )
        super().__init__(*args, **kwargs)


class MediaStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = getattr(
            settings, 'MEDIAFILES_LOCATION', 'media'
            )
        super().__init__(*args, **kwargs)
