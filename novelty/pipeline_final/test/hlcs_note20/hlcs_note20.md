---
title: "CS Notes 20"
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


<!-- page: hlcs_note20_page001 -->

# C++ Tutorials 20

# C++ Classes and Objects:

## Class

**Class ⇒** A class in C++ is the building blocks that leads to Object-Oriented programming.

## Syntax

- Class is a user-defined data type, which holds its own data members and member functions, which can be accessed and used by creating an instance of that class.
- A C++ class is like a blueprint for an object.

**Syntax ⇒**

```
Keyword - Class ClassName
{
    Access Specifier: // Can be private, public or protected
    Data Members;   // Variables to be used
    Member functions() // methods to access data member
    & Body of function;
}
```

3: // Class Name end with a semicolon.
