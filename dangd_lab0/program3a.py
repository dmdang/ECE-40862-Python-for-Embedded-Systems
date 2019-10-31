def main():
    maxNumber = int(input("How many Fibonacci numbers would you like to generate? "))
    fib(maxNumber)
    
def fib(n):
    list = []
    i = 0
    a, b = 1, 1
    while i < n:
        list.append(a)
        a, b = b, a+b
        i += 1
    print("The Fibonacci Sequence is:", str(list)[1:-1])
        
main()