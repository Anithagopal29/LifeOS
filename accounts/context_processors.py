def user_preferences(request):
    """Make dark mode, display name & the user (as `profile`) available to every template.

    The custom accounts.User model holds all per-user goals and preferences,
    so we expose it under the friendly name `profile` for the templates.
    """
    if request.user.is_authenticated:
        return {
            'dark_mode': request.user.dark_mode,
            'display_name': request.user.display_name,
            'profile': request.user,
        }
    return {'dark_mode': False, 'display_name': '', 'profile': None}
