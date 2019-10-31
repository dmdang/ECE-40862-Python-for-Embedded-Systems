from random import randint

def main():
    randNum = randint(0, 10)
    for i in range(0, 3):
        guess = int(input("Enter your guess: "))
        if guess == randNum:
            print("You win!")
            break
        if i == 2:
            print("You lose!")
            
main()
