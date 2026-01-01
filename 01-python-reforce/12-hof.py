# HOF => Funcions d'ordre superior

def require_auth(func):
    def wrapper(user):
        if user.lower() == 'admin':
            return func(user)
        else:
            return 'No tens accés'

    return wrapper

def admin_dashboard(user):
    return f'Benvingut, {user}'


auth_view = require_auth(admin_dashboard)

print(auth_view('user'))
print(auth_view('Admin'))