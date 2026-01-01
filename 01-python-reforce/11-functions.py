
def hello(greet='Hello', name = 'Guest', ):
    print(f'{greet}, {name}!')

hello('Ciao!!', 'Giovanni')
hello('Benvingut', 'Pep')
hello(name='Joan', greet='Salutacions')

def big_function(*args, **kwargs):
    print(args)
    print(kwargs)


print(big_function(3,4,6,8,9, name='Teddy', greet='Hola'))