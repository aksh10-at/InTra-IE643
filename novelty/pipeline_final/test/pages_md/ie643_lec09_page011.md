$$c(y^i,\hat{y}^i) = \text{KL}(y^i,\hat{y}^i)$$

$\to$ KL = 0 when $y^i = \hat{y}^i$, KL > 0 when $y^i \ne \hat{y}^i$

**logistic regression**

$$\min_{\text{weights of NN}} \sum_{i=1}^{N} \text{KL}(y^i,\hat{y}^i)$$

$$\min_{\text{weights}} \sum_{i=1}^{N} \text{CE}(y^i,\hat{y}^i)$$

$$E[y|x=\vec{x}] \to \text{Bernoulli r.v. likelihood}$$
