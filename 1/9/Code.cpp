#include <stdio.h>
#include <stdlib.h>

int Fibonacci(int n) {
	// codev
	if (n==1) {
		return 0;
	} else if (n==2) {
		return 1;
	} else {
		long long int f, v1, v2;
		v1 = 0; v2 = 1; f = 1;
		for (int i=3; i<n; i++) {
			v1 = v2;
			v2 = f;
			f = (v1+v2) % 1000000000;
		}
		return f;
	}
	// codev
}

int main() {
	int n; 
	while (scanf("%d", &n)>0) {
		printf("%d\n", Fibonacci(n));
	}
}
