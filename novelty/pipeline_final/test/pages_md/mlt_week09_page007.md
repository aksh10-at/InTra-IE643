$$\|w^{l+1}\|^2 = \|w^l + xy\|^2 = (w^l + xy)^T(w^l + xy) = \|w^l\|^2 + 2(w^Tx)y + \|x\|^2y^2 \le 0 \text{ because mistake}$$

$$\|w^{l+1}\|^2 \le \|w^l\|^2 + R^2$$
$$\|w^{l+1}\|^2 \le (\|w^{l-1}\|^2 + R^2) + R^2$$
$$\vdots$$
$$\|w^{l+1}\|^2 \le \|w^0\|^2 + lR^2$$

$$\boxed{\|w^{l+1}\|^2 \le lR^2} \quad \text{(no of mistakes)} \tag{①}$$

$$(w^{l+1})^Tw^* = (w^l + xy)^Tw^* = w^Tw^* + (w^{*T}x)y \ge \gamma$$

$$(w^{l+1})^Tw^* \ge w^Tw^* + \gamma$$
$$\ge (w^{l-1}w^* + \gamma) + \gamma$$
