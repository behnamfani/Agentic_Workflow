import base64
from urllib.parse import urlparse
import os


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
                {
                    "type": "text",
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": url
                    }
                }
            ]
        }
    ]


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def visual_path(query: str, path: str) -> list:
    """
    Create a message for payload to process local visual files
    :param query: User query
    :param path: path to the visual file
    :return: created message list
    """
    base64_image = encode_image(path)
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    }
                }
            ]
        }
    ]
