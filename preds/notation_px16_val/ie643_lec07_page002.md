## Recap:

$$x \in \mathbb{R}^d$$

[Diagram: A chain of fully-connected layers — input layer (column of nodes "0 0 ... 0") → $N_1$ neurons → $N_2$ neurons → $\dots$ → $N_{L-1}$ neurons → $N_L$ neurons (output layer).]

$$\hat{y} = a^L = \phi(W^L) = \phi(W^3 \phi(W^2 \phi(W^1 x)))$$

$$e(y, \hat{y}) \to \text{loss fn to compare true and predicted labels}$$