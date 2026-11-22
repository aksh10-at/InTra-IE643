[Diagram: A feedforward neural network with input layer nodes $a_1, a_2, \dots, a_c$ feeding into a hidden layer node (with multiple outgoing connections) which feeds into an output layer node producing outputs $\hat{y}_1, \hat{y}_2, \dots, \hat{y}_c$.]

$$\frac{\partial e}{\partial a_j} = \sum_{k=1}^{C} \frac{\partial e}{\partial \hat{y}_k} \cdot \frac{\partial \hat{y}_k}{\partial a_j}$$

$$= \sum_{k=1}^{C} -\frac{y_k}{\hat{y}_k} \left(\frac{\partial \hat{y}_k}{\partial a_j}\right)$$

$$e = -\sum_{j=1}^{C} y_j \log \hat{y}_j$$