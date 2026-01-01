
# and
age = 25
licensed = False

if age >= 18 and licensed:
    print('Pots conduir')

# or
is_student = False
membership = False

if is_student or membership:
    print('Tens descompte')

# not

is_admin = True
if not is_admin:
    print('No pots entrar')

# Short circuiting (corto-circuit)
name = False
print(name and name.upper())
