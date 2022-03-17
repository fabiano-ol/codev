#include <stdio.h>
#include <stdlib.h>

typedef struct E1 {
	// codev 
	char Nome[4];
	int Idade;
	// codev 
} E1;

typedef struct E2 {
	// codev 
	int Turma;
	E1 * Aluno;
	E2 * Prox;
	// codev 
} E2;

E1 V[3]; 
E2 * L;

void TestarMemoria() {
	/* Atente para o que está sendo impresso nesse teste, e 
	   elabore o programa para ser coerente com que está sendo
	   impresso aqui! */
	printf("%d %d %d\n", V[0].Idade, V[1].Idade, V[2].Idade);
	printf("%c %c %c %c\n", V[0].Nome[0], V[0].Nome[1], V[0].Nome[2], V[0].Nome[3]);
	printf("%c %c %c\n", V[1].Nome[0], V[1].Nome[1], V[1].Nome[2]);
	printf("%c %c %c\n", V[2].Nome[0], V[2].Nome[1], V[2].Nome[2]);
	printf("%d %d %d %d\n", L->Turma, L->Prox->Turma, L->Prox->Prox->Turma, L->Prox->Prox->Prox->Turma);
	printf("%d\n", L->Prox->Prox->Prox->Prox == NULL ? 1 : 0);
	printf("%d %d %d %d\n", L->Aluno->Idade, L->Prox->Aluno->Idade, L->Prox->Prox->Aluno->Idade, L->Prox->Prox->Prox->Aluno->Idade);
}

int main() {
	// codev 
	V[0].Idade = 5; V[1].Idade = 8;  V[2].Idade = 9; 
	V[0].Nome[0] = 'J'; V[0].Nome[1] = 'O'; V[0].Nome[2] = 'A'; V[0].Nome[3] = 'O'; 
	V[1].Nome[0] = 'L'; V[1].Nome[1] = 'E'; V[1].Nome[2] = 'O'; 
	V[2].Nome[0] = 'L'; V[2].Nome[1] = 'I'; V[2].Nome[2] = 'A'; 
	E2 * p; L = (E2 *) malloc(sizeof(E2)); p = L; 
	p->Turma = 1; p->Aluno = &(V[0]); p->Prox = (E2 *) malloc(sizeof(E2)); p = p->Prox;
	p->Turma = 1; p->Aluno = &(V[1]); p->Prox = (E2 *) malloc(sizeof(E2)); p = p->Prox;
	p->Turma = 2; p->Aluno = &(V[1]); p->Prox = (E2 *) malloc(sizeof(E2)); p = p->Prox;
	p->Turma = 2; p->Aluno = &(V[2]); p->Prox = NULL;
	// codev 
	TestarMemoria();
}
