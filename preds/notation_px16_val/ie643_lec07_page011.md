$$\min_{w} E = \sum_{i=1}^{N} e(y^i, \hat{y}^i) \qquad \nabla E = \sum_{i=1}^{N} \nabla e(y^i, \hat{y}^i) \to \text{very large} \to \text{over}$$

full gradient → sample-based gradient

for $k=0,1,2,\dots$
- find descent dirm using $-\nabla E(w^k)$ ($10^{-8}$)
- find a suitable step length $\alpha_k$
- $w^{k+1} \leftarrow w^k + \alpha_k(-\nabla E(w^k))$
- zero-gradient check to stop this process

$\epsilon_k$: fixed to be small value close to $10^{-5}$ / $10^{-8}$; step-length finding procedures