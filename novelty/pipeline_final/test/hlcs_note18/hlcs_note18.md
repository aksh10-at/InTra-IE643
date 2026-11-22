---
title: "CS Notes 18"
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


<!-- page: hlcs_note18_page001 -->

# C++ Tutorials (18)

Ex ⇒ `#include <iostream>`  
`using namespace std;`  
`int main()`  

```
short x = 20;
int y = x; // implicit Type Casting
```

```
cout << "The value of x" << x << endl;
cout << "The value of y" << y;
return 0;
```

## Explicit Type Casting

**2) Explicit Type Casting ⇒** When the user manually changes data from one type to another, This is known as **Explicit type casting**.

Syntax ⇒ `(data type) expression;`

```
long double → double → float → long int → unsigned int → int → short int → char
```
