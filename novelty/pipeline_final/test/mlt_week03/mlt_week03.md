---
title: "MLT Week 3"
geometry: margin=2.2cm
papersize: letter
fontsize: 10pt
header-includes:
  - \usepackage{float}
  - \floatplacement{figure}{H}
  - \usepackage{fvextra}
  - \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
  - \usepackage{cancel}
---


<!-- page: mlt_week03_page001 -->

# Introduction to Clustering

Given the data $\{X_1,\dots,X_n\} \in \mathbb{R}^d$, we want to partition it into $k$ different clusters.

There are multiple ways to partition the data into $k$ different boxes/clusters. We want to know how many ways are there in total. Naively speaking there are $n^k$ numbers of ways where $n$ is the number of data points & $k$ is the number of clusters/boxes.

Goal: performance measure of partitioning data points into clusters.

$$X_1,\dots,X_n \leftarrow \text{Data points}$$
$$Z_1,\dots,Z_n \leftarrow \text{clusters indicator}, \; z_i \in \{1,\dots,k\}$$

eg - 10th point in 4th box $\Rightarrow X_{10}$ in 4, $z_{10} \to 4$

**Question:** Given a cluster assignment, how good is it?

$$F(z_1,\dots,z_n) = \sum_{i=1}^{n}\|x_i-\mu_{z_i}\|_2^2 \quad (\text{sum of distance of each point from clusters mean})$$
$$\hookrightarrow \text{Mean/average of } z_i^{th} \text{ cluster}$$

$$\mu_k = \frac{\sum_{i=1}^{n} x_i \mathbb{I}(z_i=k)}{n} \quad (\text{average of all data points which go to the } k^{th} \text{ cluster})$$

<!-- page: mlt_week03_page002 -->

$$\sum_{i=1}^{n} 1(z_i=k) \quad \text{(cluster)} \quad (z_i=k \text{ refers to assignment in the } k^{th} \text{ cluster})$$

### Example

$\{x_1,x_2,x_3,x_4,x_5\}, \; k=2$

$z_1=1, z_2=2, z_3=1, z_4=1, z_5=2$

**5 points assigned to 2 boxes/clusters:** $x_1,x_3,x_4$ goes to 1st & $x_2,x_5$ goes into 2nd

$$\mu_1 = \frac{x_1+x_3+x_4}{3}, \; \mu_2 = \frac{x_2+x_5}{2}$$

$\therefore$ Goodness of this partition $= F(z_1,\dots,z_n)$

$$= (x_1-\mu_1)^2 + (x_2-\mu_2)^2 + (x_3-\mu_1)^2 + (x_4-\mu_1)^2 + (x_5-\mu_2)^2$$

Now that we've established a way to measure goodness,

Goal: $\min_{(z_1,\dots,z_n)} \sum_{i=1}^{n} \|x_i-\mu_{z_i}\|_2^2$

$\to$ Doing this will be difficult as there will be too many calculations ($n^k$).

<!-- page: mlt_week03_page003 -->

### K-Means Clustering (Lloyd's Algorithm)

**Initialization:** $z_1^0, z_2^0, \dots, z_n^0 \in \{1,\dots,K\}$

**Step 1:** Compute mean ($t^{th}$ iteration)
$$\Rightarrow \forall k \text{ compute } \mu_k^t = \frac{\sum_{i=1}^{n} x_i \mathbb{1}(z_i^t=k)}{\sum_{i=1}^{n} \mathbb{1}(z_i^t=k)}$$

**Step 2:** Reassignment step

```latex
\Rightarrow \forall i \; z_i^{t+1} = \argmin_k \|x_i - \mu_k^t\|_2^2 \quad \text{[if mean of current assignment is shortest, then don't reassign]}
```

*Warning: equation could not be typeset; shown as written.*


The algorithm will now run until convergence.

In the algorithm, the partition is changing in each round. There will come a point when there is no jumping of points from one partition/box/cluster [distance of each point with its own clusters' mean is strictly less than any other box's mean] then no jumping will happen & the algorithm will be said to have converged.

*Will it always converge?*
$\to$ Yes, Lloyd's Algorithm always converges.

<!-- page: mlt_week03_page004 -->

# K-Means Clustering (Lloyd's Algorithm)

However, the converged solution may not always be "optimal".
Though it does provide "reasonable" clusters in practice.

* What is the initialisation?
* What is the number of clusters/boxes that we need to use? (Value of $k$)

<!-- page: mlt_week03_page005 -->

### Convergence of K-Means Algorithm

We know that Lloyd's Algorithm always converges.

**Proof:**

Let $x_1,\dots x_l \in \mathbb{R}^d$

$$v^* = \min_{v\in\mathbb{R}^d}\sum_{i=1}^{l}\|x_i-v\|^2$$

We are looking for a vector that minimizes the over all possible vectors $v$, Sum of the distance to the bunch of points

$$v^* = \frac{1}{l}\sum_{i=1}^{l}x_i$$

---

- Let's say we are in the $t^{th}$ iteration of Lloyd's algorithm
- Current assignment:
  $$z_1^t,z_2^t,\dots,z_n^t \in \{1,\dots,k\}$$
  $\mu_k^t$ ← mean of cluster $k$ in iteration $t$
- Suppose convergence doesn't happen. We will update our assignments
  $$z_1^{t+1},z_2^{t+1},\dots,z_n^{t+1} \in \{1,\dots,k\}$$

<!-- page: mlt_week03_page006 -->

# Convergence of K-Means Algorithm

$$\sum_{i=1}^{n}\|x_i-\mu_{z_i^{t+1}}^t\|^2 \quad < \quad \sum_{i=1}^{n}\|x_i-\mu_{z_i^t}^t\|^2 \quad \text{[By algorithm's choice]}$$

mean of clusters where $x_i$ wants to go $\to$ mean of current clusters where $x_i$ is assigned

$$\sum_{i=1}^{n}\|x_i-\mu_{z_i^{t+1}}^{t+1}\|^2 \; \le \; F(z_1^{t+1},\dots,z_n^{t+1})$$

$$\Rightarrow \sum_{i=1}^{n}\sum_{k=1}^{K}\|x_i-\mu_k^{t+1}\|^2\mathbb{1}(z_i^{t+1}=k)$$

$\Rightarrow$ The objective function strictly reduces after each reassignment

$$F(z_1^{t+1},\dots,z_n^{t+1}) < F(z_1^t,\dots,z_n^t)$$

$\Rightarrow$ There are only a finite number of partitions

$\Rightarrow$ Algorithm must converge

<!-- page: mlt_week03_page007 -->

### Nature of clusters produced by K-Means

Let $K=2$. Lloyd's algorithm will produce 2 clusters with means: $\mu_1 \& \mu_2$

What can we say about the points assigned to cluster 1?

> By the algorithm's convergence, each data point in cluster 1 is now closer to $\mu_1$ than $\mu_2$: $\|x-\mu_1\|^2 \le \|x-\mu_2\|^2$

$$\|x\|^2 + \|\mu_1\|^2 - 2x^T\mu_1 \le \|x\|^2 + \|\mu_2\|^2 - 2x^T\mu_2$$
$$\|\mu_2\|^2 - \|\mu_1\|^2 \ge 2x^T(\mu_2-\mu_1)$$
$$x^T(\mu_2-\mu_1) \le \frac{\|\mu_2\|^2-\|\mu_1\|^2}{2} \quad \text{∀ } x \text{ in cluster 1}$$

![A 2D scatter plot showing two clusters — yellow shaded region labeled "Cluster 1 region" on the left, green shaded region labeled "Cluster 2 region" on the right. A dashed line from $\mu_1$ to $\mu_2$ is shown, with an arrow pointing right labeled "$(x_2-\mu_1)$". The line $x^T(\mu_2-\mu_1)=0$ is marked at the bottom.](figures/mlt_week03_page007_b1.png){width=55.0000%}

$$x^T(\mu_2-\mu_1) = \frac{\|\mu_2\|^2-\|\mu_1\|^2}{2}$$

What happens when $K=3$?

<!-- page: mlt_week03_page008 -->

# Nature of Clusters produced by K-Means

> Points in cluster $i$ will be closest to $\mu_i$ as the distance is least compared to $\mu_j$

![A central point with radii drawn to three cluster centers $\mu_1$, $\mu_2$, $\mu_3$. Each radius defines a "cluster region" — yellow for Cluster 1, green for Cluster 2, purple for Cluster 3 — as the area closer than its respective center.](figures/mlt_week03_page008_b1.png){width=55.0000%}

Cluster regions are intersections of half spaces. $(k-1)$ intersections → **Voronoi regions**

<!-- page: mlt_week03_page009 -->

### Initialization of Centroids, K-Means++

Suppose we have 1000 points & we need to put them in 5 different clusters/boxes. We can pick 5 points uniformly at random & imagine these 5 points as the cluster centers. It means that we are initializing the cluster means & not the cluster indicators ($\mu_i$, $z_j$).

Now for every datapoint we will see the closest mean & assign it to that cluster. We may have to repeat this exercise with n different means to get the best clustering. However, this is a naive way & a better way to do this is the K-Means++.

### K-Means++

# Initialization of Centroids, K-Means++

The idea behind this is that the means ($\mu_i$) should be as far away from each other as possible. If the means are close then there is no need of separate clusters, we can just make it one big cluster.

$\to$ Choose first mean $\mu_1^0$ uniformly at random from the dataset $\{x_1,\dots,x_n\}$

$\to$ For $l=2,\dots,k$ ($l \to l^{th}$ mean) choose $\mu_l^0$ probabilistically proportional to score.
$$S(x) = \min_{j=1,\dots,l-1} \|x-\mu_j^0\|^2 \; \forall x$$

### Example

Suppose we have the small dataset

<!-- page: mlt_week03_page010 -->

Suppose we have the small dataset $X = [(7,4),(8,3),(5,9),(3,3),(1,3),(10,1)]$ to which we wish to assign 3 clusters. $k=3$

We begin by randomly selecting $(7,4)$ to be a cluster center.

![A scatter plot showing a red dot at $(7,4)$, with several other points scattered around it.](figures/mlt_week03_page010_b1.png){width=55.0000%}

| $x$ | $\min(d(x,z_1)^2) \; s(x)$ |
|-----|----------------------------|
| (7,4)| -                          |
| (8,3)| 2                          |
| (5,9)| + 29                       |
| (3,3)| + 17                       |
| (1,3)| + 37                       |
| (10,1)| + 18                       |

$\frac{103}{103}$

| $x$ | prob |
|-----|------|
| (7,4)| -    |
| (8,3)| 2/103 ($\leftarrow$ lowest probability) |
| (5,9)| 29/103 |
| (3,3)| 17/103 |
| (1,3)| 37/103 |
| (10,1)| 18/103 |

$\leftarrow$ highest probability so we'll choose this as the next mean: $\mu_2^0$

![A scatter plot showing a green dot at $(3,3)$, with a red dot at $(7,4)$ and several other points scattered around them.](figures/mlt_week03_page010_b2.png){width=55.0000%}

| $x$ | $\min(d(x,z_1)^2) \; s(x)$ |
|-----|----------------------------|
| (7,4)| -                          |
| (8,3)| 2                          |
| (5,9)| + 29                       |
| (3,3)| + 4                        |
| (1,3)| -                          |
| (10,1)| + 18                       |

$\frac{53}{53}$

| $x$ | prob |
|-----|------|
| (7,4)| -    |
| (8,3)| 2/55 |
| (5,9)| 29/55 |
| (3,3)| 4/55 |
| (1,3)| -    |
| (10,1)| 18/55 |

$\leftarrow$ highest probability & the next mean: $\mu_3^0$

<!-- page: mlt_week03_page011 -->

| $x$ | prob |
| --- | --- |
| (7,4) | - |
| (8,3) | 2/55 |
| (5,9) | 29/55 |
| (3,3) | 4/55 |
| (1,3) | - |
| (10,1) | 18/55 |

$\leftarrow$ highest probability & the next mean: $\mu_3^0$

We now run k-means with initialized centers $(7,4),(1,3)$, and $(5,9)$.

# Example

| $x$ | prob |
| --- | --- |
| (7,4) | - |
| (8,3) |  |
| (5,9) | - |
| (3,3) |  |
| (1,3) | - |
| (10,1) |  |

![A scatter plot showing three red dots at $(5,9)$, $(8,3)$, and $(10,1)$, two blue dots at $(3,3)$, and one green dot at $(1,3)$, labeled $\mu_1^0$, $\mu_2^0$, $\mu_3^0$.](figures/mlt_week03_page011_b1.png){width=51.8712%}

<!-- page: mlt_week03_page012 -->

### Choice of K

Our goal is to minimize the objective function:
$$F(z_1,\dots,z_n) = \sum_{i=1}^{n}\|x_i-\mu_{z_i}\|^2$$

Let the number of clusters be the same as the number of data points. $K=n$.

How will our objective function behave then?

- If every data point will be it's own cluster then it will be the mean of that cluster. Thus the distance between $x_i$ & $\mu_{z_i}$ will be 0 & $F(z_1,\dots,z_n)=0$.
- The problem we now have is that our goal is being fulfilled as 0 is the minimum value the objective function can have but we don't want all data points to be a separate cluster as it defeats the propose of clustering.
- So we want $K$ to be as small as possible as having the largest value will minimize the objective function to zero.
- We want to penalize large values of $K$

We want to find $K$ that has the **Smallest objective function value + Penalty(K)** — Perfect balance

<!-- page: mlt_week03_page013 -->

# Choice of K

![A plot of objective function vs. $k$, with a red dashed line showing the objective, a blue solid line showing $\text{penalty}(k)$, and their sum (purple) crossing at $k^*$.](figures/mlt_week03_page013_b1.png){width=55.0000%}

Some common criterion for choosing $\boxed{\text{Obj} + \text{Penalty}}$

- **AIC** - Akaike Information Criterion: $2k - 2\log(L(\hat{\theta}^*))$
- **BIC** - Bayesian Information Criterion: $k(\log n) - 2\log(L(\hat{\theta}^*))$
