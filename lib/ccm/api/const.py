'''
Shared constants
'''

class _APIResponse:
    """
    predefined API response
    """

    @property
    def OK(self):
        return {
            'state': 'ok',
        }.copy()

APIResponse = _APIResponse()  # singleton
