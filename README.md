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

# Features

What's the difference between this and \<insert package name\>?
Well, unlike alternatives and homebrew solutions, this package:
- Has progressbar!
- Does not crash when stopped using Ctrl+C or "Stop" button in Jupyter
- Works in Wandows
- Continues working if stumbled upon occasional exception (i.e. you won't have to rerun whole process just because record #451673 out of 100M is broken)
- Properly works with Series

# Examples

## Parallelizing map and list comprehension

```
def some_fun(x):
    return x ** 2
x = [1, 2, 3]

# Single-thread variants
y = [some_fun(i) for i in x]
y = map(some_fun(i) for i in x)

# Parallelized variant
y = parallelize(x, some_fun)
```

## Parallel for
It is a bit clumsy to use because it requires multithreading.Manager to create
process-shared lists, but so far it's best way to implement `pfor`.

```
# Single-thread variant
result = []
for x in range(10):
    result.append(x ** 2)
print(result)
    
# Parallelized variant
from multithreading import Manager

with Manager() as m:
    l = m.list()
    for x in pfor(range(10)):
        l.append(x ** 2)
    print(l)
```

# What's under the hood?

This package uses `multiprocessing` to launch new threads and processes. It means that there is no GIL-circumvention
logic. Thus, all GIL-related quirks are present. For example, you might not get expected speed-up if your functions
do not spend much time in I/O.

# Installation

Run

`pip3 install git+https://github.com/rampeer/py-parallelize --user`

or

`sudo pip3 install git+https://github.com/rampeer/py-parallelize`
