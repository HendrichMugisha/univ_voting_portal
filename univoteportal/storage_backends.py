from storages.backends.s3boto3 import S3Boto3Storage


# ---------------------------------------------------------
# STATIC FILE STORAGE (optional — only if you ever want S3
# to handle static files instead of WhiteNoise)
# ---------------------------------------------------------
class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True   # static files can be overwritten during deploy


# ---------------------------------------------------------
# MEDIA FILE STORAGE  (this is the important one)
# ---------------------------------------------------------
class MediaStorage(S3Boto3Storage):
    location = 'media'            # matches AWS_LOCATION in settings.py
    default_acl = 'public-read'   # file can be accessed publicly
    file_overwrite = False        # avoid replacing existing uploads
