#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void PermutacaoCircular(char A[], int n, int k) {
	// codev
	char c = A[0]; char pc; 
	int j=0; int ji = 0;
	for (int i=0; i<n; i++) {
		pc = A[(j+k)%n];
		A[(j+k)%n] = c;
		j = (j+k)%n;
		c = pc;
		if (j==ji) {
			ji = ji+1;
			j = ji;
			c = A[ji]; 
		}
	}
	// codev
}

int main() {
	int n,k; 
	char * A; 
	while (scanf("%d %d", &n, &k)>0) {
		A = (char *) malloc(sizeof(char)*(n+600000));
		scanf("%s", A);
		PermutacaoCircular(A, n, k);
		printf("%s\n", A);
		free(A);
	}
}
