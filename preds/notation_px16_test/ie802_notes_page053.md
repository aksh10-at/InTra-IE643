# Heuristics for MINLO

## Initial/Construction Heuristic

- Feasibility Pump (expensive)
  $\hookrightarrow$ Sounding (sophisticated)
- RINS
- Local Branching

**MILP Case:** (pure binary)

$$\min c^Tx \quad Ax \le b \quad x \in \{0,1\}^n$$

① Solve the LP:
$$\begin{cases} \min c^Tx \\ Ax \le b \\ 0 \le x \le 1 \end{cases} \Rightarrow \hat{x}$$

$\hookrightarrow$ If fractional $\to$ round it to nearest integer

$\hookrightarrow$ Not always works

**Simple Sounding of $\hat{x}$:**
$$\text{rounding of } \hat{x} = \begin{bmatrix} \lfloor x_1 \rfloor & \text{if } x_1 < 0.5, \; \text{or}, \; \lceil x_1 \rceil \\ \vdots \\ \lfloor x_n \rfloor & \text{or}, \; \lceil x_n \rceil \end{bmatrix} \Rightarrow \min_{x \in \{0,1\}^n} \|x-\hat{x}\|_1 \; \text{and } Ax \le b$$

② $\min_{i=1}^{n} |x_i - \hat{x}_i|$ — rounding of $(\hat{x})$
$\hat{x} \to$ LP relaxation soln

$$\text{e.g.: } \hat{x} = \begin{bmatrix} 0 \\ 1 \\ 0.4 \\ 0.6 \\ 0.8 \\ 0.1 \end{bmatrix} \qquad \text{sndng }(\hat{x}) = \begin{bmatrix} 0 \\ 1 \\ 0 \\ 1 \\ 1 \\ 0 \end{bmatrix}$$

$\hookrightarrow$ not working, if looser, try again

becomes
$$\min|x_1-0|+|x_2-1|+\cdots+|x_6-1| \quad \text{st } Ax \le b, \; 0 \le x \le 1$$

$$\min x_1+(1-x_2)+x_3+(1-x_4)+(1-x_5)+x_6 \quad \text{st } Ax \le b, \; 0 \le x \le 1$$

$\star$ if $\hat{x} = \begin{bmatrix} 0.1 \\ 0.9 \\ 0 \\ 0 \\ 0 \end{bmatrix}$, $\to$ again round off gives same soln $\to$ we have to stop heuristic and flip some variables.