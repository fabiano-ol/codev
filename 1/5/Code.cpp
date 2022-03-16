#include <stdio.h>
#include <stdlib.h>
#include <math.h>

double ContaMisteriosa(int n) {
	// codev
	double v = 0.0;
	int dezn = pow(10,n);
	double m1 = 1.0;
	for (int k = 1; k <= dezn; k++) {
		v += m1/(2*k-1);
		m1 = -m1;
	}
	return 4*v;
	// codev
}

int main() {
	int n;  
	while (scanf("%d", &n)>0) {
		printf("%.8f\n", ContaMisteriosa(n));
	}
}
