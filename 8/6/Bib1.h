
using namespace std;

template <typename T>
struct FilaPrioridade {
	priority_queue<T> Q;
	int n_max;
};

template <typename T>
void Constroi(FilaPrioridade<T> &F, int n) {
	F.Q = priority_queue<T>();
	F.n_max = n;
}

template <typename T>
int Tamanho(FilaPrioridade<T> &F) {
	return F.Q.size();
}

template <typename T>
void Enfileira(FilaPrioridade<T> &F, T x) {
	if (F.Q.size() < F.n_max) {
		F.Q.push(x);
	} else {
		throw std::runtime_error("Capacidade da fila de prioridade excedida.");
	}
}

template <typename T>
T Desenfileira(FilaPrioridade<T> &F) {
	T x = F.Q.top(); F.Q.pop(); return x;
}

template <typename T>
T Proximo(FilaPrioridade<T> &F) {
	return F.Q.top(); 
}

template <typename T>
void Destroi(FilaPrioridade<T> &F) {
	return;
}



