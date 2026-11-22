$$\frac{\partial e}{\partial z_i^l} = \frac{\partial e}{\partial a_i^l} \left(\frac{\partial a_i^l}{\partial z_i^l}\right) = \frac{\partial e}{\partial a_i^l} \cdot \phi'(z_i^l)$$

$$\frac{\partial e}{\partial a_i^l} = \sum_{m=1}^{N_{l+1}} \frac{\partial e}{\partial z_m^{l+1}}$$

[Diagram: A neuron $i^{th}$ neuron of layer $l$, labeled $a_i^l$, feeding into $N_{l+1}$ neurons of layer $l+1$, labeled $z_m^{l+1}$ and $a_m^{l+1}$.]