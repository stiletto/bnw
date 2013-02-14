from bnw_handlers.base import require_auth


@require_auth
def cmd_whoami(request):
    return dict(ok=True, user=request.user['name'])
