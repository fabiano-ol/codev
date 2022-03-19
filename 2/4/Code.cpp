#include <stdio.h>
#include <stdlib.h>

typedef struct No {
	int E;
	No * Prox;
} No;

int Ultimo(No * L) {
	// codev
	if (L == NULL) {
		return -1;
	} else {
		No * p = L;
		while (p->Prox != L)  {
			p = p->Prox;
		}
		return p->E;
	}
	// codev
}

void InsereCircular(No * &L, int e, No * &u) {
	No * novo = (No *) malloc(sizeof(No));
	novo->E = e;
	if (L == NULL) {
		novo->Prox = novo;
		L = novo;
	} else {
		novo->Prox = L;
		u->Prox = novo;
	}
	u = novo;
}

int main() {
	No * L = NULL; No * u; 
	printf("%d\n", Ultimo(L));
	InsereCircular(L,1,u);
	printf("%d\n", Ultimo(L));
	InsereCircular(L,2,u);
	printf("%d\n", Ultimo(L));
	for (int i=3; i<=2000000; i++) {
		InsereCircular(L,i,u);
	}	
	printf("%d\n", Ultimo(L));
	return 0;
}
