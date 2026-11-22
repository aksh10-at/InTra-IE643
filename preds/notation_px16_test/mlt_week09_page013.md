$$= \sum_{i=1}^{n} \left[-x_i + y_ix_i + x_i\frac{e}{1+e^{-w^Tx_i}}\right]$$

$$= \sum_{i=1}^{n} \left[y_ix_i - x_i\left(\frac{1}{1+e^{-w^Tx_i}}\right)\right]$$

$$\nabla \log L(w) = \sum_{i=1}^{n} \left[x_i(y_i-\frac{1}{1+e^{-w^Tx_i}})\right]$$

## Gradient update rule,

$$w_{t+1} = w_t + \eta_t \nabla \log L(w)$$
$$= w_t + \eta_t \left(\sum_{i=1}^{n} [x_i(y_i-\frac{1}{1+e^{-w_t^Tx_i}})]\right)$$

[Diagram: A neuron $x_i \in \mathbb{R}^d$ feeding into a sigmoid neuron $g(w_t^Tx_i)$ with output $\theta_i$, labeled $\{0,1\}$ — the neuron's activation.]

## Regularized version

$$\min_w \sum_{i=1}^{n}\left[\log(1+e^{w^Tx_i}) + w_i^Tx_i(1-y_i)\right] + \frac{\lambda}{2}\|w\|^2$$

cross validate hyperparameters. Regularizer.