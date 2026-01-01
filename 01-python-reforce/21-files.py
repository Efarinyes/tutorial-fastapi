

try:
    with open('test.txt',mode='w') as my_file:
        text = my_file.write('Hola Mon!!!')
    with open('test.txt', mode='r+') as my_file:
        print(my_file.readlines())
        text = my_file.write('Adeu Mon!!! ')
    with open('test.txt', mode='r') as my_file:
        print(my_file.readlines())

except FileNotFoundError:
    print('File not found.')
except Exception as err:
    print(f'Hi hagut un error: {err}')