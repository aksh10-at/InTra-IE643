## Convex MINLO Case (Pure Binary)

$$\min c^Tx+d^T\gamma$$
$$g_i(x,\gamma)\le0 \quad \forall i$$
$$x\in\mathbb{R}^n, \; \gamma\in\{0,1\}^p \to \text{continuous}$$

① solve NLP relaxation $\Rightarrow$ get $\hat{x},\hat{\gamma}$ → bound of $\boxed{?}$

② min $\sum_{i=1}^{p}|y_i-\text{round}(\hat{y}_i)|$
st $g_i(x,y)\le0$, $0\le y\le1$

$\Leftrightarrow$ MILP $\Rightarrow$ ...

$\gamma\in\{0,1\}^p$

**Non-convex MINLO Case (Pure Binary)**

$\Rightarrow$ Leave it ...

---

**RINS Heuristic** (Relaxed-Induced Nbhd Search) → Improvement

**Convex MILO:** Let $(\hat{x},\hat{\gamma})$ be known solution of MINLO.

[Diagram: A tree with root node branching into two subtrees, each further branching.]

① solve NLP relaxation of that node $\Rightarrow (\hat{x},\hat{\gamma})$, $\hat{\gamma}\notin\mathbb{Z}^p$ → if majority of equal, randomly fix

search nbhd of it, $(\hat{y}_i=\hat{y}_i)$

② comp. $\hat{y}$ and $\hat{\gamma}$ → all those same → fix it

③ solve the smaller MINLO → don't solve fully, put time limits ex. 5 sec., and some other parameters.

Node limited