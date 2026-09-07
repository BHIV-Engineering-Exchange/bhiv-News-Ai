import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastapi import UploadFile


@dataclass
class StoredUpload:
    file_path: str
    size_bytes: int
    sha256: str


class LargeFileHandler:
    """
    Disk-backed upload handler for large files.

    The uploaded file is read in bounded chunks instead of
    loading the complete file into RAM.

    Responsibilities:
    - Chunked upload processing
    - Incremental SHA-256 fingerprinting
    - Maximum file-size enforcement
    - Temporary disk storage
    - Bounded upload memory usage
    """

    DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB

    DEFAULT_MAX_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB

    @classmethod
    async def store_upload(
        cls,
        upload: UploadFile,
        filename: str,
        chunk_size: Optional[int] = None,
        max_size: Optional[int] = None,
    ) -> StoredUpload:

        chunk_size = chunk_size or cls.DEFAULT_CHUNK_SIZE

        max_size = max_size or int(
            os.getenv(
                "MAX_UPLOAD_SIZE_BYTES",
                str(cls.DEFAULT_MAX_SIZE),
            )
        )

        suffix = Path(filename).suffix.lower()

        temp_file = tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=suffix,
            prefix="samachar_ingest_",
            delete=False,
        )

        file_path = temp_file.name

        sha256 = hashlib.sha256()
        total_size = 0

        try:
            while True:
                chunk = await upload.read(chunk_size)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_size:
                    raise ValueError(
                        f"File exceeds maximum allowed size "
                        f"of {max_size} bytes"
                    )

                temp_file.write(chunk)

                sha256.update(chunk)

            temp_file.flush()

            return StoredUpload(
                file_path=file_path,
                size_bytes=total_size,
                sha256=sha256.hexdigest(),
            )

        except Exception:
            try:
                os.unlink(file_path)
            except OSError:
                pass

            raise

        finally:
            temp_file.close()