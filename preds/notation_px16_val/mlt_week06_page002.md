# Cross-validation for minimizing MSE

$$\text{trace}[(XX^T)^{-1}] \quad [\text{sum of diagonal entries}] \quad \text{also} \quad [\text{sum of eigenvalues of matrix}]$$

Let the Eigenvalues of $XX^T$ be $\{\lambda_1,\dots,\lambda_d\}$.
$\therefore$ Eigenvalues of $(XX^T)^{-1}: \left\{\frac{1}{\lambda_1},\dots,\frac{1}{\lambda_d}\right\}$

Mean Squared Error ($\hat{w}_{ML}$) = $E[\|\hat{w}_{ML}-w\|^2]$
= $\sigma^2 \sum_{i=1}^{d} \frac{1}{\lambda_i}$

---

For some matrix $A$, let eigenvalues be $\{\lambda_1,\dots,\lambda_d\}$.

Then what are the eigenvalues of $(A+\lambda I)$? = $\{\lambda_1+\lambda,\dots,\lambda_d+\lambda\}$

$\hookrightarrow \in \mathbb{R}_{+ve}$, $\hookrightarrow \in \mathbb{R}^{d\cdot d}$

$$\text{trace}(XX^T+\lambda I)^{-1} = \left(\sum_{i=1}^{d} \frac{1}{\lambda_i+\lambda}\right)$$

---

We want to decrease MSE by reducing the value of trace. How do we find this $\lambda \in \mathbb{R}_+$?

By the method of **cross validation**

[Diagram: A horizontal line divided into "training set" (left) and "validation set" (right).]