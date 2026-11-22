## Train a perceptron:

$$D = \{(x^t, y^t)\} \quad (\text{Online learning}), \quad t=1,2,3,\dots$$

$\to \tilde{w}^0 = 0$

$\to t=0,1,2,3,\dots$

$\to$ receive a sample $(x^t,y^t) \in D$

$\to \tilde{x}^t = \begin{bmatrix} x^t \\ 1 \end{bmatrix}$

$\to \hat{y}^t = \text{Perceptron}(\tilde{x}^t; \tilde{w}^t)$ (Prediction)

**Update rule:**

if $\hat{y}^t = y^t$: no update, $\tilde{w}^{t+1} = \tilde{w}^t$
else: $\boxed{\tilde{w}^{t+1} = \tilde{w}^t + y^t \tilde{x}^t}$