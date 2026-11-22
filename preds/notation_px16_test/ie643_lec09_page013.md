[Diagram: A chain of layers — input layer $\hat{y}_1,\hat{y}_2,\dots,\hat{y}_C$ through a fully-connected layer (black arrow) to output layer $\hat{y}_j$, with $\sum_j \hat{y}_j = 1$.]

$$a_1^L \leftarrow \theta, \quad a_2^L \leftarrow \phi, \quad \vdots, \quad a_C^L \leftarrow \psi$$

$$\hat{y}_j = \frac{\exp(a_j^L)}{\sum_k \exp(a_k^L)}, \qquad R=1$$

**Soft-max function**

$$\hat{y}_j = \frac{\exp(a_j^L)}{\sum_k \exp(a_k^L)}$$

min-max scaling: 0 → 1.