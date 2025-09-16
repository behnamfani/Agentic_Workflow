import base64


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
