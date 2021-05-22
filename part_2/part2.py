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

df = pd.read_csv('Student_marks_list.csv')
df['sum'] = df.sum(axis=1)              #time taken to calculate sum is O(rows * columns)
data = np.array(df)

print('----------------------------------------------------------------')
print('Method 1')
print('----------------------------------------------------------------')
max_indices = np.argmax(data, axis=0)       #time taken to find topper in each subject is O(n)
print("Topper in maths is",data[max_indices[1]][0])
print("Topper in Biology is", data[max_indices[2]][0])
print("Topper in English is", data[max_indices[3]][0])
print("Topper in Physics is", data[max_indices[4]][0])
print("Topper in Chemistry is", data[max_indices[5]][0])
print("Topper in Hindi is", data[max_indices[6]][0])
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
Topper in maths is Manasa
Topper in Biology is Sreeja
Topper in English is Praneeta
Topper in Physics is Sagar
Topper in Chemistry is Manasa
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
