
# Decorators

def require_auth(func):
    def wrapper(user):
        if user.lower() == 'admin':
            return func(user)
        else:
            return 'No tens accés'

    return wrapper


@require_auth
def admin_dashboard(user):
    return f'Benvingut, {user}'


print(admin_dashboard('user'))
print(admin_dashboard('Admin'))

