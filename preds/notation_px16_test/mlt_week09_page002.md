$$i \in \{1,\dots,n\}, n_i \in \mathbb{R}$$

Iteration:
$$w^0 = 0 \in \mathbb{R}^d \qquad [0 \; 0 \; 0 \; \dots \; 0]$$

until convergence,
- Pick $(x_i,y_i)$ pair from the dataset
- If $\text{sign}(w^T x_i) = \text{sign}(y_i)$, do nothing
else,
$$w^{t+1} = w^t + x_i y_i \qquad \leftarrow \text{update rule}$$