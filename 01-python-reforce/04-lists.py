
list_numbers = [1, 2, 3, 4, 5, 4, 6, 4,  7, 8, 4, 9, 10]
list_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
list_mix = [1, 'a', 'c', 3, True, [1, 3, 5], 5.5]

shopping_card = ['Mac mini', 'Iphone 17', 'Airpad Pro']

# print(type(shopping_card))

## Mètodes

# Append
print(list_numbers)
list_numbers.append(1000)
print(list_numbers)

# Remove
list_numbers.remove(5)
print(list_numbers)

# Count

print(list_numbers.count(4))
