from src.utils.logging_config import get_logger


def updates_steaming(chunk: dict, token_usage: dict) -> tuple[str, dict]:
    """
    Streaming tool calling and updates of React agent as well as total token used ({'Input': 0, 'Output': 0})
    """
    final_content = ""
    for chunk_type, chunk_data in chunk.items():
        get_logger().info(f"Update Type: {chunk_type}")
        if 'messages' in chunk_data:
            for message in chunk_data['messages']:
                # Handle AI messages
                if hasattr(message, 'content') and message.content:
                    content = message.content
                    if isinstance(message.content, list):
                        content = message.content[0]['text']
                    if content.strip():
                        get_logger().info(f"Content: {content}")
                        final_content = content
                # Handle tool calls
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        get_logger().info(
                            f"Tool Call: {tool_call['name']} with args: {tool_call['args']}")
                # Handle tool responses
                if hasattr(message, 'name') and hasattr(message, 'tool_call_id'):
                    get_logger().info(f"Tool Response from {message.name}: {message.content}")
                # Track token usage
                meta = getattr(message, 'response_metadata', None) if not isinstance(message,
                                                                                        dict) else message.get(
                    'response_metadata')
                if meta and 'token_usage' in meta:
                    tu = meta['token_usage']
                    token_usage['Output'] += tu.get('completion_tokens', 0)
                    token_usage['Input'] += tu.get('prompt_tokens', 0)
            get_logger().info(f"--"*10 + "\n")
    return final_content, token_usage
