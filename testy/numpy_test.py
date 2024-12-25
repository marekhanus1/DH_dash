import numpy as np

# Initial data
a = ([False, False, True, True, True, True], ['241129', 3000, 10], [False, False], [[480, 1020], 2, 4, 4, 30, [1410, 1420]])

for element in a:
    for j in element:
        print(j)
        print(type(j))

a = ([False, False, True, True, True, True], ['241129', 3000, 10], [False, False], ['08:00-17:00', 2, 4, 4, 30, '23:50-23:59', '23:59'])
# remove last element: '23:59'

a = list(a)
a[-1] = a[-1][:-1]
print(a)