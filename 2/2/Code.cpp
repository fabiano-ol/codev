#include <stdio.h>
#include <stdlib.h>

typedef struct No {
	int E;
	No * Prox;
} No;

// codevremove
int max(int a, int b) {
	return (a<b ? b : a);
}
// codevremove

int Maior(No * L) {
	// codev
	int m = L->E;
	No * p = L->Prox;
	while (p != NULL) {
		m = max(m, p->E);
		p = p->Prox;
	}
	return m;
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
	Insere(L,-1000000000);
	printf("%d\n", Maior(L));
	Insere(L,2);
	printf("%d\n", Maior(L));
	for (int i=3; i<=1000000; i++) {
		Insere(L,i);
	}	
	printf("%d\n", Maior(L));
	return 0;
}
