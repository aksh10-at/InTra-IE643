[Diagram: A chain of fully-connected layers (left) vs. a fully-connected layer feeding into a chain of output neurons (right).]

$$\delta^l = (W^{l+1})^T \; \text{diag}(\phi'^{l+1}) \cdot \delta^{l+1}$$

fwd pass: error is CE.

bckwd pass: ??