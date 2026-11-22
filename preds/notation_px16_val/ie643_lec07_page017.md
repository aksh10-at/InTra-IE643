[Diagram: A feedforward neural network — input layer neuron connects via $w_{ij}^l$ to $i^{th}$ neuron in layer $l$, which connects to another neuron.]

$i^{th}$ neuron in layer $l$

$j^{th}$ neuron in layer $l-1$: $w_{ij}^l = \dots$

$$\frac{\partial e}{\partial w_{ij}^l} = \frac{\partial e}{\partial z_i^l} \cdot \boxed{\frac{\partial z_i^l}{\partial w_{ij}^l}}$$

**forward chain rule**

$$z_i^l = \sum_{k=1}^{N_{l-1}} w_{ik}^l a_k^{l-1}$$
$$a_i^l = \phi(z_i^l)$$

$$\frac{\partial e}{\partial z_i^l} = \frac{\partial e}{\partial a_i^l} \cdot \frac{\partial a_i^l}{\partial z_i^l} = \frac{\partial e}{\partial a_i^l} \cdot \phi'(z_i^l)$$