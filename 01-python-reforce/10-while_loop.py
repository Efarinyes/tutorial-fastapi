"""
counter = 1
while counter <= 10:
    print(f'Number: {counter}')
    counter += 1
else:
    print('Done')
"""

response = ''
while response.lower() != 'bye':
    print(response)
    response = input('Escriu "bye" per sortir: ')
else:
    print('Done')