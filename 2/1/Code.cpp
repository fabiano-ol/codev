#include <stdio.h>
#include <stdlib.h>

typedef struct No {
	int E;
	No * Prox;
} No;

int NumeroElementos(No * L) {
	// codev
	int n = 0;
	No * p = L;
	while (p != NULL) {
		n = n+1;
		p = p->Prox;
	}
	return n;
	// codev
}

void Insere(No * &L, int e) {
	No * novo = (No *) malloc(sizeof(No));
	novo->E = e;
	novo->Prox = L;
	L = novo;
}

int main() {
	No * L = NULL; 
	printf("%d\n", NumeroElementos(L));
	Insere(L,1);
	printf("%d\n", NumeroElementos(L));
	Insere(L,2);
	printf("%d\n", NumeroElementos(L));
	for (int i=3; i<=1000000; i++) {
		Insere(L,i);
	}	
	printf("%d\n", NumeroElementos(L));
	return 0;
}
