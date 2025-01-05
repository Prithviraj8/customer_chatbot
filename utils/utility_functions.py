def format_response(content: str) -> str:
    """Format the response content to ensure consistent styling."""
    # Remove multiple consecutive newlines
    import re
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Ensure proper spacing around code blocks
    content = re.sub(r'```(\w+)\n', r'\n```\1\n', content)
    content = re.sub(r'\n```\n', r'\n```\n\n', content)

    return content.strip()