class sumFinder:
    def findIndex(self, list, target):
        dictionary = {}
        for i, value in enumerate(list):
            if target - value in dictionary:
                return(dictionary[target - value], i)
            if i == 6:
                return(999, 999)
            dictionary[value] = i

def main():
    a = [10, 20, 10, 40, 50, 60, 70]
    targetNum = int(input("What is your target number? "))
    b, c = sumFinder().findIndex(a, targetNum)
    if b == 999 and c == 999:
        print("index1=N/A, index2=N/A")
    else:
        print("index1=" + str(b) + "," + " index2=" + str(c))

main()

            
            
        
        