#include <algorithm>

typedef struct Par {
	int x, y;
} Par;

void Ordenar(Par B[], int N) {
	std::sort(B, B+N, [](Par p1, Par p2) {
		return (p1.x < p2.x) || ((p1.x == p2.x) && (p1.y < p2.y));
	});
}
