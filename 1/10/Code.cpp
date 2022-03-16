#include <stdio.h>
#include <stdlib.h>

void RepresentacaoDecimal(long long int n, int R[], int & k) {
	// codev
	if (n==0) {
		R[0] = 0; k=1;
	} else {
		k = 0;
		while (n>0) {
			R[k] = n%10;
			n = n/10;
			k = k+1;
		}
		for (int i=0; i<k/2; i++) {
			int t = R[i];
			R[i] = R[k-1-i];
			R[k-1-i] = t;
		}
	}
	// codev
}

int main() {
	long long int n; 
	int R[16]; int k;
	while (scanf("%lld", &n)>0) {
		RepresentacaoDecimal(n, R, k);
		printf("%d\n", k);
		for (int i=0; i<k; i++) {
			printf("%d ", R[i]);
		}
		printf("\n");
	}
}
