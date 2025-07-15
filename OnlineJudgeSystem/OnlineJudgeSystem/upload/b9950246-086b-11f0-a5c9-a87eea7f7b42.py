arr=[1,5,2,6,4,3]
for i in range(len(arr)):
	for j in range(len(arr) - i - 1):
		if arr[j] > arr[j + 1]:
			arr[i], arr[j + 1] = arr[j + 1], arr[j]
print(arr)
