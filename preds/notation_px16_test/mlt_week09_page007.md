$$\|w^{l+1}\|^2 = \|w^l + xy\|^2$$
$$= (w^l + xy)^T(w^l + xy)$$
$$= \|w^l\|^2 + 2(w^{l^T}x)y + \|x\|^2y^2$$

$$\le R^2 \quad \text{because mistake}$$

$$\|w^{l+1}\|^2 \le \|w^l\|^2 + R^2$$
$$\|w^{l+1}\|^2 \le (\|w^{l-1}\|^2 + R^2) + R^2$$
$$\vdots$$
$$\|w^{l+1}\|^2 \le \|w^0\|^2 + lR^2$$

$$\boxed{\|w^{l+1}\|^2 \le lR^2} \quad \text{(no. of mistakes)}$$

$$(w^{l+1})^Tw^* = (w^l + xy)^Tw^*$$
$$= w^{l^T}w^* + (w^{*^T}x)y$$
$$\ge \gamma$$

$$(w^{l+1})^Tw^* \ge w^{l^T}w^* + \gamma$$
$$\ge (w^{l-1^T}w^* + \gamma) + \gamma$$