# Parallelize

This package lets you parallelize computations, in parallel-map fashion.

![Screenshot](screenshot.png)

# Features

What's the difference between this and \<insert package name\>?
Well, unlike alternatives and homebrew solutions, this package:
- Has progressbar!
- Does not crash when stopped using Ctrl+C or "Stop" button in Jupyter
- Works in Wandows
- Continues working if stumbled upon occasional exception (i.e. you won't have to rerun whole process just because record #451673 out of 100M is broken)
- Properly works with Series

# Examples

```
x = [1, 2, 3]
y = parallelize(x, some_fun)
```

Is equivalent to

```
x = [1, 2, 3]
y = [some_fun(i) for i in x]
```

but the function `some_fun` is executed in multithreaded fashion.

# Installation

Run

`pip3 install git+https://github.com/rampeer/py-parallelize --user`

or

`sudo pip3 install git+https://github.com/rampeer/py-parallelize`
