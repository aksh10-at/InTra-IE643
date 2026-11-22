# Perceptron Learning Algorithm

## Discriminative Model for Classification

How to model $P(y=1|x)$?

Simplest assumption: $P(y=1|x) = \begin{cases} 1 & \text{if } w^Tx \ge 0 \\ 0 & \text{otherwise} \end{cases}$

$\therefore$ Data is Linearly Separable.

[Diagram: Two scatter plots — one with a linear separator (green vs red dots on either side, labeled "Linear separate exists"), the other with overlapping clusters ("No linear separator", "Dataset is not allowed under our model").]

Can we develop algorithms with the assumption that the data is linearly separable?

$$\text{Goal: } \min_{h \in H_{\text{linear}}} \sum_{i=1}^{n} \Pi(h(x_i) \ne y_i) \qquad H_{\text{linear}} = \{ h_w: h_w(w) = \text{sign}(w^Tx) \}$$

assuming "Linear Separability"

---

## Perceptron Algorithm

Input: $\{(x_1,y_1),\dots,(x_n,y_n)\}, \; x_i \in \mathbb{R}^d, \; y_i \in \{+1,-1\}$