from random import randint
print("1")
print("-10000000")
print("2")
print("-10 -8")
print("2")
print("0 -1")
n = 100000
for i in range(10):
	print(n)
	for j in range(n):
		if j > 0:
			print(' ', end='')
		print(randint(-(10**3),10**3), end='')
	print()
