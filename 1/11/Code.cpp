#include <stdio.h>
#include <stdlib.h>

// codevremove
void Imprime(int R[], int k) {
	printf("%d\n", k);
	for (int i=0; i<k; i++) {
		printf("%d ", R[i]);
	}
	printf("\n");
}

void Inverte(int R[], int k) {
	for (int i=0; i<k/2; i++) {
		int t = R[i];
		R[i] = R[k-1-i];
		R[k-1-i] = t;
	}
}
// codevremove

void Soma(int A[], int n, int B[], int m, int R[], int &k) {
	// codev 
	Inverte(A,n); Inverte(B,m); /*mais fácil fazer a operação com os vetores em ordem inversa */ 
	k = 0;
	int vaium = 0;
	while ((k<n) || (k<m) || (vaium == 1)) {
		int a, b; a=0; b=0;
		//printf("k=%d; n=%d m=%d\n", k, n, m);
		if (k<n) {
			a = A[k];
		}
		if (k<m) {
			b = B[k];
		}
		//printf("a=%d; b=%d;vaium=%d\n", a, b, vaium);
		R[k] = (a+b+vaium)%10;
		vaium = (a+b+vaium)/10;
		k = k+1;
	}
	Inverte(A,n); Inverte(B,m); Inverte(R,k); 
	// codev
}


int main() {
	int n, m; 
	
	int * A, * B, *R; int k;
	A = (int *) malloc(sizeof(int)*1000);
	B = (int *) malloc(sizeof(int)*1000);
	R = (int *) malloc(sizeof(int)*1000*1000);
	while (scanf("%d %d", &n, &m)>0) {
		for (int i=0; i<n; i++) {
			scanf("%d", &A[i]);
		}
		for (int i=0; i<m; i++) {
			scanf("%d", &B[i]);
		}
		Soma(A, n, B, m, R, k);  Imprime(R, k);
	}
	free(A); free(B); free(R);
}
