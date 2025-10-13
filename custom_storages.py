from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Custom storage for static files.
    Reads the location from settings.STATICFILES_LOCATION if defined.
    Ensures files are publicly readable.
    """
    location = getattr(settings, 'STATICFILES_LOCATION', 'static')
    default_acl = 'public-read'
    # Optional: prevent S3 from adding its own ACL if using bucket policy
    file_overwrite = True
    querystring_auth = False  # ensures URLs are clean without signed params


class MediaStorage(S3Boto3Storage):
    """
    Custom storage for media files.
    Reads the location from settings.MEDIAFILES_LOCATION if defined.
    Ensures files are publicly readable and don't overwrite existing files.
    """
    location = getattr(settings, 'MEDIAFILES_LOCATION', 'media')
    default_acl = 'public-read'
    file_overwrite = True
    querystring_auth = False
