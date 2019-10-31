def main():
    birthdays = {'Albert Einstein':'03/14/1879', 'Benjamin Franklin':'01/17/1706', 'Ada Lovelace':'12/10/1815'}
    print("Welcome to the birthday dictionary. We know the birthdays of:")
    print("Albert Einstein")
    print("Benjamin Franklin")
    print("Ada Lovelace")
    name = str(input("Who's birthday do you want to look up?\n"))
    if name in birthdays:
        print(name + "'s birthday is", birthdays[name] + ".")

main()

