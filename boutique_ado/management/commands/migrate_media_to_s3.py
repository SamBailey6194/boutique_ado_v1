from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from pathlib import Path


class Command(BaseCommand):
    help = "Upload all local media files to the default storage (S3)."

    def handle(self, *args, **kwargs):
        media_root = Path(settings.MEDIA_ROOT)
        files_uploaded = 0

        for file_path in media_root.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(media_root).as_posix()
                with open(file_path, 'rb') as f:
                    if not default_storage.exists(relative_path):
                        default_storage.save(relative_path, f)
                        files_uploaded += 1
                        self.stdout.write(f"Uploaded {relative_path}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished uploading {files_uploaded} files to storage."
                )
            )
