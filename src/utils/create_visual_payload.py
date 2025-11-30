import base64
from urllib.parse import urlparse
import os
from typing import List, Union


def is_url(path: str) -> bool:
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https", "ftp")


def is_local_path(path: str) -> bool:
    return os.path.exists(path)


def visual_public_url(query: str, url: str) -> list:
    """
    Create a message for payload to process public visual url
    :param query: User query
    :param url: Public URL to the visual file
    :return: created message list
    """
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {"type": "image_url", "image_url": {"url": url}},
            ],
        }
    ]


def _get_mime_type_from_path(file_path: str) -> str:
    """
    Determine MIME type from file extension.
    Falls back to 'image/png' if unknown.
    """
    extension = file_path.lower().split('.')[-1]
    mime_types = {
        # Image types
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp',
        # Video types
        'mp4': 'video/mp4',
        'avi': 'video/avi',
        'mov': 'video/quicktime',
        'wmv': 'video/x-ms-wmv',
        'flv': 'video/x-flv',
        'webm': 'video/webm',
        'mkv': 'video/x-matroska',
        '3gp': 'video/3gpp',
        # Document types
        'pdf': 'application/pdf',
        # Audio types
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'flac': 'audio/flac',
        'ogg': 'audio/ogg',
    }
    return mime_types.get(extension, 'image/png')


def _encode_file_to_base64(path: str) -> str:
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def create_file_analysis_message(file_path: Union[str, List[str]], query: str | None = None) -> list:
    """
    Create a message for visual/document/audio analysis.

    Supports images, videos, PDFs, and audio files. Accepts a single path or a list of paths.
    Returns a list with one message dict to match other helpers in this module.

    Args:
        file_path (str | list): path or list of paths to files
        query (str | None): optional text query to include alongside files

    Returns:
        list: [ { "role": "user", "content": [ ...file entries... ] } ]
    """
    def build_file_content(fp: str) -> dict:
        if not os.path.exists(fp):
            raise FileNotFoundError(f"File not found: {fp}")

        file_data = _encode_file_to_base64(fp)
        mime_type = _get_mime_type_from_path(fp)
        filename = os.path.basename(fp)

        if mime_type.startswith('image/'):
            content_type = 'image'
        elif mime_type.startswith('video/'):
            # Some APIs treat videos as image-type content or separate video type;
            # keep 'image' for compatibility with image+frame extraction flows.
            content_type = 'image'
        elif mime_type == 'application/pdf':
            content_type = 'file'
        elif mime_type.startswith('audio/'):
            content_type = 'audio'
        else:
            content_type = 'file'

        file_content = {
            'type': content_type,
            'source_type': 'base64',
            'data': file_data,
            'mime_type': mime_type,
        }

        if content_type == 'file':
            file_content['filename'] = filename

        return file_content

    content = []
    if isinstance(file_path, list):
        for fp in file_path:
            content.append(build_file_content(fp))
    else:
        content.append(build_file_content(file_path))

    # Include optional text query as first content item if provided
    message_content = []
    if query:
        message_content.append({'type': 'text', 'text': query})
    message_content.extend(content)

    message = {
        'role': 'user',
        'content': message_content,
    }

    return [message]


# Example usage:# 
query = "Please analyze the following files."
path = r"B:\Codes\Python\CODE\Agentic_Workflow\Agentic_Workflow\notebooks\lama.jpg"
payload = create_file_analysis_message(path, query)
print(payload)