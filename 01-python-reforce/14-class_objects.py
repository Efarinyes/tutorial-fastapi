
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def work(self):
        return f'{self.name} treballa molt'


person1 = Person('Bob', 25)
person2 = Person('John', 30)

print(person1.work())
print(person2.work())