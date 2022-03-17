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

void Subtrai(int A[], int n, int B[], int m, int R[], int &k) {
	// codev
	Inverte(A,n); Inverte(B,m); /*mais fácil fazer a operação com os vetores em ordem inversa */ 
	k = 0;
	while (k<n) {
		int j=k;
		while ((A[j] < 0) || ((j < m) && (A[j] < B[j]))) {
			A[j] = A[j]+10;
			A[j+1] = A[j+1]-1;
			j = j+1;
		}
		R[k] = A[k]-B[k];
		k = k+1;
	}
	if ((R[k-1] == 0) && (k>1)) {
		k = k-1;
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
		Subtrai(A, n, B, m, R, k);  Imprime(R, k);
	}
	free(A); free(B); free(R);
}
