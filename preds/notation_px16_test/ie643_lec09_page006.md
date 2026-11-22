$$\hat{y} = \begin{bmatrix} \hat{y}_1 \\ \hat{y}_2 \\ \vdots \\ \hat{y}_C \end{bmatrix}, \quad (x,y) \; \text{or} \; y \in \{1,2,\dots,C\}$$

Transform discrete $y$ into a $C$-dim vector.

$$y=k \in \{1,2,\dots,C\} \to \text{one "hot" vector} \begin{bmatrix} 0 \\ \vdots \\ 1 \\ 0 \\ \vdots \\ 0 \end{bmatrix} \to k^{th} \text{ component}$$

$$e(\hat{y},y) \; \text{(prediction true label)}$$