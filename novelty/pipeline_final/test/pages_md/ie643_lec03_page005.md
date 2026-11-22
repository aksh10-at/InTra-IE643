# Train a perceptron:

$$D = \{(x^t, y^t)\} \quad (\text{online learning}), \qquad t=1,2,3,\dots$$

$\to \vec{w}^0 = \vec{0}$

$\to t=0,1,2,3,\dots$

$\to$ receive a sample $(x^t,y^t) \in D$

$\to \hat{x}^t = \begin{bmatrix} x^t \\ 1 \end{bmatrix}$

$\to \hat{y}^t = \text{Perceptron}(\hat{x}^t, \vec{w}^t)$ [Prediction]

**Update rule:**

if $\hat{y}^t == y^t$: no update, $\vec{w}^{t+1} = \vec{w}^t$
else: $\vec{w}^{t+1} = \vec{w}^t + y^t\hat{x}^t$
