---
title: "CS Notes 19"
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


<!-- page: hlcs_note19_page001 -->

# C++ Tutorials (19)

Ex ⇒

## C++ Basics

```
#include <iostream>
using namespace std;

int main()
{
    double x = 1.2;
    int y = (int)x; // Explicit type casting
    cout << "Value of y = " << y;
    return 0;
}
```

```
double x = 1.2;
double y = 3.45;
double z = 6.78;
```
