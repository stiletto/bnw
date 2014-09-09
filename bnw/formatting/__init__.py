import plaintext,moinmoin,markdown

formats = {
    'moinmoin': moinmoin.MoinMoinFormat(),
    'plaintext': plaintext.PlainTextFormat(),
    'markdown': markdown.MarkdownFormat(),
}

def thumbify(text, format=None, secure=False):
    """Format text and generate thumbs using available formatters.

    :param format: default: 'markdown'. Specify text formatter.
                   Variants: 'moinmoin', 'markdown' or None,
                   which fallbacks to markdown.

    Return: (formatted_text, thumbs)
    Thumbs: list of (original_file_url, thumb_url)
    """
    if format not in formats:
        format = 'plaintext'
    return formats.get(format).format(text, secure)


def linkify(text, format='markdown'):
    """Only do text formatting. See :py:meth:`thumbify`."""
    return thumbify(text, format=format)[0]
