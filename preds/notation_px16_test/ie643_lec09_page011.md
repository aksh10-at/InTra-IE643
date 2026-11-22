$$e(y^i,\hat{y}^i) = KL(y^i,\hat{y}^i) \to KL=0 \text{ when } y^i=\hat{y}^i; \quad KL>0 \text{ when } y^i\ne\hat{y}^i$$

$$\min_{\text{weights of NN}} \sum_{i=1}^{N} KL(y^i,\hat{y}^i)$$

$$\min_{\text{weights}} \sum_{i=1}^{N} CE(y^i,\hat{y}^i)$$

[Diagram: A chain from "logistic regression" down to $\mathbb{E}[y|x=x]$, then to Bernoulli r.v. likelihood.]

$$\boxed{\mathbb{E}[y|x=x]}$$