
using namespace std;

typedef struct FilaPrioridade {
	priority_queue<int> Q;
	int n_max;
} FilaPrioridade;

void Constroi(FilaPrioridade &F, int n) {
	F.Q = priority_queue<int>();
	F.n_max = n;
}

int Tamanho(FilaPrioridade &F) {
	return F.Q.size();
}

void Enfileira(FilaPrioridade &F, int x) {
	if (F.Q.size() < F.n_max) {
		F.Q.push(x);
	} else {
		throw std::runtime_error("Capacidade da fila de prioridade excedida.");
	}
}

int Desenfileira(FilaPrioridade &F) {
	int x = F.Q.top(); F.Q.pop(); return x;
}

int Proximo(FilaPrioridade &F) {
	return F.Q.top(); 
}

void Destroi(FilaPrioridade &F) {
	return;
}



