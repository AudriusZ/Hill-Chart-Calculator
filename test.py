number = [-3, -3.5, -2.5, -1.5, 2, 3, 13]
number_new = []

for i in number:
    new = int(i) if i < 0 else int(i) + 1
    
    number_new.append(new)

print(number_new)