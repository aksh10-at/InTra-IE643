## Parameter regime

**Stochastic gradient descent**

$$D = \{(x^i,y^i)\}_{i=1}^{N}$$

$\to w^0$

$\to$ for $k=0,1,2,\dots$

$\hookrightarrow$ Compute a **stochastic gradient**
- Randomly choose $j\in\{1,2,3,\dots N\}$
- Compute $\nabla e(y^j,\hat{y}^j)$

$$w^{k+1} \leftarrow w^k + n_k \nabla e(y^j,\hat{y}^j)$$

**Stochastic approx. 51** $\to$ Convergence to the local opt/saddle pt.

might not lead to descent