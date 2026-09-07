from typing import Iterator


class TextChunker:
    """
    Splits large text into bounded chunks for NLP processing.

    Chunking is an internal processing optimization.
    The original input fingerprint remains unchanged.
    """

    DEFAULT_CHUNK_SIZE = 50_000
    DEFAULT_OVERLAP = 500

    @classmethod
    def chunks(
        cls,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ) -> Iterator[str]:

        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        if not text:
            return

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(
                start + chunk_size,
                text_length,
            )

            chunk = text[start:end]

            if chunk.strip():
                yield chunk

            if end >= text_length:
                break

            start = end - overlap