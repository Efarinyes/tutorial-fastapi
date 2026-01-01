
def divide_number():
    try:
        a = int(input('Introdueix numerador: '))
        b = int(input('Introdueix denominador: '))

        result = a / b

    except ZeroDivisionError:
        print('No pots dividir per zero, soca')

    except ValueError:
        print('Només puc dividir números, atontat')

    except Exception as error:
        print(error)
    else:
        print(result)
        return result
    finally:
        print('Acabat')

divide_number()


