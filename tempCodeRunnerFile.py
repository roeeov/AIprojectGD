i = 2
while True:
    is_prime = True
    for num in range(2, i-1):
        if i % num == 0:
            is_prime = False
    if is_prime: print(i)
    i += 1

     