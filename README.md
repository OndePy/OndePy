# OndePy ![status](https://img.shields.io/badge/status-beta-orange)
A Python easy-to-use reactive framework

> [!WARNING]
> for the moment, OndePy is only a project and is very limited.

## What even is OndePy ?
> OndePy is an easy-to-use, efficient, developper-friendly, but minimalist reactive framework. A reactive framework allows you to observe a value, and do special actions if the value changes. It's rather like intelligent gotos.

## How do one get OndePy ?
Unfortunately, beacause PyPi is horrible to use and because I'm alone making this project, to use OndePy, you must (for the moment) download all the files (excepting the LICENCE and Readme of course) in this repo, open a command shell (cmd, PowerShell, bash, zsh...), place your working directory at the location of the setup.cfg and pyproject.toml, and run:
```(Bash)
$ pip install .
```

## How do one use OndePy ?
Here is a full specification for OndePy framework:

### 1. Set an observable value
> This value will be stalked throughout the program.

To set an observable value, we use the function ```state()``` \
example:
```(Python)
import onde

price = onde.state(100)
```
price is now state as a _State class object that, among others, contains the value 100. It is quite same as ```price = 100```, but here we will be able to trigger events depending on observations \
To access and edit the value stored on ```price```, we can call the attribute ```value``` of the ```_State``` class. \
Example:
```(Python)
import onde

price = onde.state(100)
price.value = 120
```
To finish with, we have a few special methods that can be applied to a _State object, such as ```undo()```/```redo()``` that reverses the last value, or restores a value that has been undid, and then do like we added this value manually: it trigers the events if we set events. Then we have ```silent_undo()```/```silent_redo()``` that make just like ```undo()```/```redo()```, but don't trigger the events. \
Example of use:
```(Python)
import onde

price = onde.state(100)
price.value = 120
price.value = 140
price.undo()
```

### 2. Compute a value automatically
In python, when you make
```(Python)
def add(1, 5): return a+b
print(add(1, 5))
```
the call of ```add()``` inside of ```print()``` automatically calculates at this time a+b. But with a reactive framework, we can make it even faster, calculating a+b everytimes a or be changes. We will just have a different logic. \
Here is an example written in Pseudo-Python:
```(Python)
a = state(1)
b = state(5)

[a thing that tells it must be computed automatically at every single change of a or b]
a + b
```
With OndePy, the thing that tells it must be computed automatically is a decorator, ```@computed```, what means we must enwrap a function into it.\ 
We will hence do the previous example like:
```(Pyhton)
import onde

a = onde.state(1)
b = onde.state(5)

@onde.computed
def total(): return a.value + b.value
```

### 3. Trigger something on the change of an observable value
with the decorator ```@effect```, you can trigger a function when any observable value changes. \ 
For instace, you can do:

```(Pyhton)
import onde

price = onde.state(100)
tax = onde.state(0.2)

@onde.computed
def total():
    return price.value * (1 + tax.value)

@onde.effect
def show():
    print("Total Price: ", total())

price.value = 120
```

Here, as soon as price changes, the new total is calculted by ```@computed```, and showed by ```@effect```
