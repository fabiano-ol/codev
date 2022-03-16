#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int QtdePrimos(int n) {
	// codev
	int q = 0;
	for (int i = 2; i <= n; i++) {
		bool ehPrimo = true;
		for (int j=2; j<=sqrt(i); j++) {
			if (i%j == 0) {
				ehPrimo = false; break;
			}
		}
		if (ehPrimo) {
			q += 1;
		}
	}
	return q;
	// codev
}

int main() {
	int n;  
	while (scanf("%d", &n)>0) {
		printf("%d\n", QtdePrimos(n));
	}
}
