# Parallelize

This package lets you parallelize computations.

![Screenshot](screenshot.png)

It is a:
- drop-in replacemenet for `map`, `apply`, and `for`.
- wrapper around `multiprocessing`.
- quick and relatively tidy way to parallelize computations
- nice choice if your data does not fit into dask's data model, but you do not want to write enormous amounts of code
using raw joblib/multitask/ipyparallel : everything is wrapped neatly here

It is **NOT** a great idea to use this package if:
- you will rely heavily on parallel computations, or need something more than plain `map` (for example, computation graphs). 
Please refer to [dask](https://dask.org/), as it provides mode functionality.
- you are starting project from scratch, using Jupyter and have a spare hour or two. In this case please spend this time
productively by getting used to verbose but fantastic [ipyparallel](https://ipyparallel.readthedocs.io/en/latest/) API.
- you are operating primarily with numpy arrays / vectorized operations. [Numba](http://numba.pydata.org/) is a great 
fit for such tasks.

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

# Features

What's the difference between this and \<insert package name\>?
Well, unlike alternatives and homebrew solutions, this package:
- Has progressbar!
- Does not crash when stopped using Ctrl+C or "Stop" button in Jupyter
- Works in Wandows
- Continues working if stumbled upon occasional exception (i.e. you won't have to rerun whole process just because record #451673 out of 100M is broken)
- Properly works with Series

# What's under the hood?

This package uses `multiprocessing` to launch new threads and processes. It means that there is no GIL-circumvention
logic. Thus, all GIL-related quirks are present. For example, you might not get expected speed-up if your functions
do not spend much time in I/O.

# Installation

Run

`pip3 install git+https://github.com/rampeer/py-parallelize --user`

or

`sudo pip3 install git+https://github.com/rampeer/py-parallelize`
