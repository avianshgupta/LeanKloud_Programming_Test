import numpy as np
import pandas as pd

def bestThree(arr, n, c):
    '''
    Output: return the names of best three students in the class
    Time Complexity: O(n)
    '''
    if (n < 3):
        print("Invalid Input")
        return
    first = second = third = -1
    nfirst = nsecond = nthird = ''
    for i in range(n):
        if (arr[i][c] > first):
            third = second
            second = first
            first = arr[i][c]
            nthird = nsecond
            nsecond = nfirst
            nfirst = arr[i][0]
        elif (arr[i][c] > second):
            third = second
            second = arr[i][c]
            nthird = nsecond
            nsecond = arr[i][0]
        elif (arr[i][c] > third):
            third = arr[i][c]
            nthird = arr[i][0]
    return nfirst, nsecond, nthird

def subjectTopper(arr, n, c):
    '''
    Output: a list of students with maximum marks
    Time Complexity: O(n)
    '''
    maxm = max(arr[:,c])
    toppers = [i for i in range(n) if arr[i][c] == maxm]
    return [arr[i][0] for i in toppers]
    


df = pd.read_csv('Student_marks_list.csv')
subjects = list(df.keys()[1:])
df['sum'] = df.sum(axis=1)              #time taken to calculate sum is O(rows * columns)
data = np.array(df)

print('----------------------------------------------------------------')
print('Method 1')
print('----------------------------------------------------------------')

for i in range(1,data.shape[1]-1):
    toppers = subjectTopper(data, data.shape[0], i)         #time taken to find the toppers in each subject is O(n)
    if len(toppers) == 1:
        print("Topper in",subjects[i-1],"is",end=" ")
    else:
        print("Toppers in",subjects[i-1],"are",end=" ")
    print(*toppers, sep=', ', end='\n')
top3 = bestThree(data, data.shape[0], 7)    #time taken to find best three students in the class is O(n)
print("Best students in the class are %s %s %s" %(top3[0], top3[1], top3[2]))
print('----------------------------------------------------------------')
print('Method 2')
print('----------------------------------------------------------------')
print("Topper in maths is",np.array(df.nlargest(1, 'Maths'))[0][0])
print("Topper in Biology is", np.array(df.nlargest(1, 'Biology'))[0][0])
print("Topper in English is", np.array(df.nlargest(1, 'English'))[0][0])
print("Topper in Physics is", np.array(df.nlargest(1, 'Physics'))[0][0])
print("Topper in Chemistry is", np.array(df.nlargest(1, 'Chemistry'))[0][0])
print("Topper in Hindi is", np.array(df.nlargest(1, 'Hindi'))[0][0])

print("Best Student in the class are",end=" ")
for row in np.array(df.nlargest(3, 'sum')):
    print(row[0], end=" ")
print()

'''
OUTPUT
----------------------------------------------------------------
Method 1
----------------------------------------------------------------
Topper in Maths is Manasa
Topper in Biology is Sreeja
Topper in English is Praneeta
Toppers in Physics are Sagar, Mehuli
Toppers in Chemistry are Manasa, Vivek
Topper in Hindi is Aravind
Best students in the class are Manodhar Bhavana Sourav
----------------------------------------------------------------
Method 2
----------------------------------------------------------------
Topper in maths is Manasa
Topper in Biology is Sreeja
Topper in English is Praneeta
Topper in Physics is Sagar
Topper in Chemistry is Manasa
Topper in Hindi is Aravind
Best Student in the class are Manodhar Bhavana Sourav

'''
