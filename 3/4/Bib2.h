
/*
typedef struct No {
	int E;
	No * Prox;
} No;
*/

typedef struct Fila {
	No * Prox;
	No * Ult;
	int N;
} Fila;

void Constroi(Fila &F) {
	F.Prox = NULL; F.Ult = NULL; F.N = 0;
}

void Enfileira(Fila &F, int x) {
	No * n = (No *) malloc(sizeof(No));
	n->E = x;
	n->Prox = NULL;
	if (F.Ult == NULL) {
		F.Prox = n;
		F.Ult = n;
	} else {
		F.Ult->Prox = n;
		F.Ult = n;
	}
	F.N++;
}

int Desenfileira(Fila &F) {
	No * n = F.Prox; int x = n->E;
	F.Prox = F.Prox->Prox;
	if (F.Prox == NULL) F.Ult = NULL;
	free(n);
	F.N--;
	return x;
}

int Proximo(Fila &F) {
	return F.Prox->E;
}

int Tamanho(Fila &F) {
	return F.N;
}

void Destroi(Fila &F) {
	while (Tamanho(F) > 0) {
		Desenfileira(F);
	}
}
