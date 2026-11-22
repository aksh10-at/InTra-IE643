# Maths coverage of the fine-tuned model (final_clean)

Held-out pages (val + test): 107. LaTeX commands or environments used in their labels: 85. Never in the train labels: 4. In fewer than 3 train pages: 9.

## Display equations on the 76 test pages, by error class

| class | equations | share |
|---|---|---|
| exact | 41 | 21% |
| notation | 1 | 1% |
| near | 42 | 21% |
| structure | 72 | 37% |
| missing | 41 | 21% |
| all | 197 | |

exact + notation = the maths is right, only the way of writing it differs from the label.

## Commands in held-out labels: train pages, held-out pages, model recall

| command | train pages | held-out pages with it | model wrote it on those pages |
|---|---|---|---|
| `\text` | 137 | 44 | 39/44 |
| `\in` | 99 | 38 | 38/38 |
| `\sum` | 84 | 38 | 37/38 |
| `\dots` | 101 | 35 | 32/35 |
| `\frac` | 75 | 33 | 33/33 |
| `\mathbb` | 73 | 33 | 30/33 |
| `\hat` | 64 | 31 | 29/31 |
| `\begin` | 70 | 26 | 24/26 |
| `\end` | 70 | 26 | 24/26 |
| `\left` | 58 | 26 | 18/26 |
| `\right` | 58 | 26 | 18/26 |
| `\quad` | 85 | 25 | 23/25 |
| `\rightarrow` | 79 | 24 | 13/24 |
| `env:bmatrix` | 59 | 22 | 21/22 |
| `\leq` | 64 | 20 | 19/20 |
| `\geq` | 56 | 19 | 17/19 |
| `\min` | 42 | 19 | 19/19 |
| `\to` | 54 | 17 | 8/17 |
| `\vdots` | 52 | 15 | 14/15 |
| `\cdot` | 34 | 14 | 13/14 |
| `\leftarrow` | 24 | 13 | 9/13 |
| `\nabla` | 23 | 12 | 10/12 |
| `\alpha` | 29 | 11 | 8/11 |
| `\mu` | 15 | 11 | 11/11 |
| `\partial` | 18 | 11 | 11/11 |
| `\gamma` | 14 | 10 | 6/10 |
| `\langle` | 27 | 10 | 9/10 |
| `\rangle` | 27 | 10 | 9/10 |
| `\underbrace` | 12 | 10 | 0/10 |
| `\boxed` | 27 | 9 | 3/9 |
| `\log` | 16 | 9 | 9/9 |
| `\qquad` | 37 | 9 | 3/9 |
| `\phi` | 41 | 8 | 8/8 |
| `\vec` | 16 | 8 | 6/8 |
| `\Rightarrow` | 26 | 7 | 6/7 |
| `\ell` | 7 | 6 | 2/6 |
| `\forall` | 37 | 6 | 5/6 |
| `\lambda` | 24 | 6 | 6/6 |
| `\neq` | 11 | 6 | 6/6 |
| `\beta` | 9 | 5 | 4/5 |
| `\eta` | 7 | 5 | 4/5 |
| `\infty` | 11 | 5 | 5/5 |
| `\therefore` | 10 | 5 | 5/5 |
| `\tilde` | 4 | 5 | 4/5 |
| `\bar` | 1 | 4 | 3/4 |
| `\cup` | 1 | 4 | 3/4 |
| `\downarrow` | 14 | 4 | 4/4 |
| `\theta` | 19 | 4 | 3/4 |
| `\times` | 29 | 4 | 4/4 |
| `env:cases` | 10 | 4 | 4/4 |
| `\Big` | 8 | 3 | 0/3 |
| `\cdots` | 42 | 3 | 1/3 |
| `\delta` | 6 | 3 | 3/3 |
| `\epsilon` | 11 | 3 | 3/3 |
| `\hookrightarrow` | 10 | 3 | 2/3 |
| `\lim` | 5 | 3 | 3/3 |
| `\max` | 18 | 3 | 3/3 |
| `\operatorname` | 5 | 3 | 0/3 |
| `\sigma` | 17 | 3 | 3/3 |
| `\Leftrightarrow` | 5 | 2 | 1/2 |
| `\dfrac` | 9 | 2 | 0/2 |
| `\equiv` | 6 | 2 | 0/2 |
| `\exists` | 5 | 2 | 1/2 |
| `\exp` | 4 | 2 | 2/2 |
| `\mathcal` | 2 | 2 | 0/2 |
| `\prod` | 11 | 2 | 2/2 |
| `\sqrt` | 20 | 2 | 2/2 |
| `\subseteq` | 1 | 2 | 2/2 |
| `\Phi` | 0 | 1 | 0/1 |
| `\Theta` | 0 | 1 | 0/1 |
| `\ddots` | 2 | 1 | 0/1 |
| `\iff` | 3 | 1 | 0/1 |
| `\lceil` | 2 | 1 | 1/1 |
| `\lfloor` | 3 | 1 | 0/1 |
| `\longrightarrow` | 2 | 1 | 0/1 |
| `\ni` | 0 | 1 | 1/1 |
| `\notin` | 0 | 1 | 1/1 |
| `\otimes` | 4 | 1 | 0/1 |
| `\propto` | 5 | 1 | 1/1 |
| `\rceil` | 2 | 1 | 1/1 |
| `\rfloor` | 3 | 1 | 0/1 |
| `\sim` | 5 | 1 | 1/1 |
| `\underline` | 3 | 1 | 0/1 |
| `\uparrow` | 12 | 1 | 1/1 |
| `env:pmatrix` | 2 | 1 | 0/1 |

## Examples per class (label | prediction)

### notation
- ie643_lec09_page015: `\delta^L = \begin{bmatrix} \partial e/\partial a_1^L \\ \partial e/\partial a_2^L \\ \vdot` | `\delta^L = \begin{bmatrix} \frac{\partial e}{\partial a_1^L} \\ \frac{\partial e}{\partial`

### near
- ie643_lec03_page001: `y^i \in \{ +1, -1 \} =: \mathcal{Y}` | `y^i \in \{+1,-1\} =: Y`
- ie643_lec03_page001: `h : \mathcal{X} \rightarrow \mathcal{Y}` | `h: X \to Y`
- ie643_lec03_page002: `\tilde{w} = \begin{bmatrix} w_1 \\ w_2 \\ w_3 \\ \vdots \\ w_d \\ -\theta \end{bmatrix}` | `\tilde{W} = \begin{bmatrix} w_1 \\ w_2 \\ w_3 \\ \vdots \\ w_d \\ \theta \end{bmatrix}`
- ie643_lec03_page003: `\vec{w} = \begin{bmatrix} w_1 \\ w_2 \\ \vdots \\ w_d \end{bmatrix} \qquad \vec{x} = \begi` | `\tilde{w} = \begin{bmatrix} w_1 \\ w_2 \\ \vdots \\ w_d \end{bmatrix}, \quad \tilde{x} = \`
- ie643_lec03_page003: `\langle \vec{w}, \vec{x} \rangle - \theta \geq 0 \; ; \; < 0` | `\langle \vec{w}, \vec{x} \rangle - \theta \geq 0`
- ie643_lec03_page003: `\langle \tilde{w}, \tilde{x} \rangle \geq 0 \; ; \; < 0` | `\langle \tilde{w}, \tilde{x} \rangle \geq 0`

### structure
- ie643_lec03_page001: `x^i = \begin{bmatrix} x^i_1 \\ x^i_2 \\ \vdots \\ x^i_d \end{bmatrix} \in \mathbb{R}^d =: ` | `D = \{(x^i,y^i)\}_{i=1}^{N<\infty}, \quad x^i = \begin{bmatrix} x_1^i \\ x_2^i \\ \vdots \`
- ie643_lec03_page003: `\tilde{w} = \begin{bmatrix} w_1 \\ w_2 \\ w_3 \\ \vdots \\ w_d \\ -\theta \end{bmatrix}_{d` | `\tilde{w} = \begin{bmatrix} w_1 \\ w_2 \\ w_3 \\ \vdots \\ w_d \\ -\theta \end{bmatrix}, \`
- ie643_lec03_page003: `\sum_{j=1}^{d} w_j x_j \geq \theta \; ; \; < \theta \quad \text{(decision rule)}` | `\sum_{j=1}^{d} w_j x_j \geq 0 \; (\geq 0) \quad \text{decision rule}`
- ie643_lec03_page006: `\text{sign}(z) = +1, \; z \geq 0; \quad -1, \; \text{otherwise}` | `\text{sign}(z) = +1, z \geq 0`
- ie643_lec03_page006: `\tilde{w} = \begin{bmatrix} 1 \\ 1 \\ -4 \end{bmatrix} \qquad \tilde{x} = \begin{bmatrix} ` | `\tilde{w} = \tilde{w} + y \tilde{x} = \begin{bmatrix} 1 \\ -4 \end{bmatrix} + \begin{bmatr`
- ie643_lec03_page006: `\tilde{w} = \begin{bmatrix} 1 \\ 1 \\ -4 \end{bmatrix} + \begin{bmatrix} 2 \\ 1 \\ 1 \end{` | `\tilde{w} = \tilde{w} + y \tilde{x} = \begin{bmatrix} 1 \\ -4 \end{bmatrix} + \begin{bmatr`

### missing
- ie643_lec03_page001: `\mathcal{D} = \{ (x^i, y^i) \}_{i=1}^{N < \infty}` | `D = \{(x^i,y^i)\}_{i=1}^{N<\infty}, \quad x^i = \begin{bmatrix} x_1^i \\ x_2^i \\ \vdots \`
- ie643_lec03_page005: `\tilde{w}^{t+1} = \tilde{w}^t` | `D = \{(x^t, y^t)\} \quad (\text{online learning}), \qquad t=1,2,3,\dots`
- ie643_lec03_page005: `\tilde{w}^{t+1} = \tilde{w}^t + y^t \tilde{x}^t` | `D = \{(x^t, y^t)\} \quad (\text{online learning}), \qquad t=1,2,3,\dots`
- ie643_lec03_page006: `\tilde{w} = \tilde{w} + y\tilde{x}` | `x_1 + x_2 = 4`
- ie643_lec03_page007: `3x_1 + 2x_2 = 3` | `3x_1 + 2x_2 = 3 \rightarrow \begin{bmatrix}3\\2\\-3\end{bmatrix}, \begin{bmatrix}2\\1\end{`
- ie643_lec09_page002: `\rightarrow \frac{\partial e}{\partial a_i^l} \cdot \phi'(z_i^l)` | `\frac{\partial e}{\partial a_i^l} = \sum_m \frac{\partial e}{\partial a_m^{l+1}} \phi'(z_m`


## Symbol level (test, all maths on each page as a bag of symbols)

Decorations (\mathcal, \vec, \tilde, \hat, \bar, \boxed, \underbrace, \text) and spacing are ignored,
and \to = \rightarrow, \le = \leq. So this counts symbols that are read wrong, dropped or invented.

- Symbols in the labels: 7977. Precision 0.884, recall 0.906, F1 0.895.
- Most often dropped: `_` 60, `\ell` 42, `^` 41, `1` 32, `x` 30, `i` 26, `y` 26, `t` 22, `w` 21, `\rightarrow` 21, `-` 18, `0` 18, `2` 18, `n` 16, `=` 16
- Most often added: `l` 48, `i` 47, `t` 46, `1` 45, `a` 44, `x` 43, `r` 41, `\rightarrow` 37, `e` 34, `n` 30, `b` 30, `m` 30, `s` 25, `c` 24, `_` 23

## What this means and what to do (22 Nov 2026)

- Symbol reading is already good: about 90% of the maths symbols on a test page are read right
  (F1 0.895). The single biggest symbol error is a writing convention, not a misread: the labels
  write `\ell` and the model writes `l` (42 dropped, 48 added). The rest of the "added" letters
  are mostly words inside `\text{...}` that the label writes differently.
- Most equation-level errors are not misread symbols. They are (1) grouping, where the model writes
  two label equations as one display block or splits one, (2) labelling conventions (`\mathcal{X}`
  vs `X`, `\underbrace`, `\boxed`, `\dfrac`), and (3) a few real slips (a dropped minus sign,
  a wrong subscript).
- Only 4 commands in the held-out labels never occur in training (`\Phi`, `\Theta`, `\ni`,
  `\notin`) and 9 occur on fewer than 3 training pages.

Would public handwritten-maths data help?
- Datasets: MathWriting (Google, about 230k human-written plus synthetic expressions, online ink),
  CROHME (about 10k expressions, ink), HME100K (100k photographed expressions), Aida (synthetic
  calculus). Licences differ (several are non-commercial research only), so check each before use.
  The ink datasets must first be rendered to images.
- They teach reading single expressions. That would help the rare and unseen symbols and the real
  slips. It would not fix grouping or our labelling conventions, which are most of the remaining
  equation errors, and it may pull the model towards their LaTeX style.
- The pipeline for it already exists: `00_dataset/build_external_dataset.py` (images + labels.json
  -> JSONL with EQUATION_PROMPT) and `combine_with_core.py` (mixes it in with a cap).

Recommended order (all after the assessment, as new runs with their own names, test once):
1. Cheap, likely gain: make label notation consistent (one form for `\ell`, `\to`, `\frac`,
   `\mathcal` sets) and retrain (about 1 h), or at least add these synonyms to the equation metric.
2. Targeted external data: a few thousand MathWriting/CROHME expressions that contain the rare
   symbols, mixed at most 1 external per 3 own examples as a second task. About 2-3 h including
   rendering and training. Compare on validation with the paired bootstrap.
3. A full-scale external mix only if step 2 shows a gain.

## Update: notation rescore (step 22 in NOTES.md)
Scoring with one notation on both sides: NED 0.311 -> 0.302, exact equation match 0.137 -> 0.168,
equation F1 0.338 -> 0.354. Notation explains a small part of the maths error, so the retrain on
consistent labels was not run. See notation_rescore.md.
