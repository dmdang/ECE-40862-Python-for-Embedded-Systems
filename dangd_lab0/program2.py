def main():
    a = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    newList = []
    print("a =", a)
    number = int(input("Enter number: "))
    for i in a:
        if i >= number:
            break
        newList.append(i)
    print("The new list is", newList)

main()
        