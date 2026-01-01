class Person:
    species = 'Human'
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self._energy = 100
        self.__password = '1234'

    # Mètode protegit
    def _waste_energy(self, quantity):
        self._energy -= quantity
        return self._energy

    # Mètode privat
    def __generate_password(self):
        return f'$${self.name}{self.age}$$'


    def work(self):
        return f'{self.name} treballa molt'

person1 = Person('Bob', 20)
print(person1.work())
print(person1.name)
print(person1._waste_energy(20))
# print(person1.__password()) # Mètode privat. No accessible fàcilment
print(person1._Person__password) #Manera d'accedir a un atribut privat
print(person1._Person__generate_password()) #Manera d'accedir a un mètode privat