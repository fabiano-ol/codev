#include <stdio.h>
#include <stdlib.h>

long long int CalculaSoma(int n) {
	// codev
	long long int s = (1+n);
	s = s*n/2;
	return s;
	// codev
}

int main() {
	int n;
	while (scanf("%d", &n)>0) {
		printf("%lld\n", CalculaSoma(n));
	}
}
