# Pigeon

Welcome, pigeon is an interpreted programming language written in python, it was written in five days (yes you read that right) by me. This programming language doesn't do anything 'special' or 'different', it's just basically something i built to satisfy my thirst for knowledge on how programming languages are built. So because of this the programming language is quite limited.


## Setup

You need python 3.12+ to be able to run this language (you have been warned), if you don't have it then go download it. if you already have it just clone this repo

`git clone http://github.com/duckdoe/pigeon.git`

cd into the folder `cd pigeon/`, once your in this folder run the example program in this folder

Windows:
`python pigeon.py example.pg`

Linux & Mac
`python3 pigeon.py example.pg`

You can edit the *example.pg* file if you want

*If you can don't try to rid my code ;)*


## Guide

This is a quick guide that should introduce you to all the features of my programming language

### Datatypes

In this langauge we have the basic datatypes such as string, numbers, boolean, array, maps and null

```
"duck" 'duck' // single-line strings

`
This is a multi-line
string
` // this is a multi-line string

12 1.2 // Numbers

true false // booleans

[1, "duck", true] // arrays

{name: "duck", age: 15} // maps

null // speaks for itself
```

### Variables

A variable can either be mutable or immutable

**Note**: A mutable variable's value can be changed and that of an immutable variable cannot be changed

```
let age = 12 // mutable
const name = "duck" // immutable

age = 13 // re-assigning works
name = "jumper" // re-assigning returns an error

// We also have shorthand assignment operations

age += 1 // 13
age -= 1 // 12
age /= 1 // 12
age *= // 12

// We also have postfix operators
age-- // 11
age++ // 12
```

### Control Flow
if, else if, else statements for control flow

```
if true {
    ..
} else if false {
    ...
} else {
    ...
}
```

### Loops
we have for and while loops

```
// while loops

while true{
    ...
}

for let i = 0; i < 10; i++ {
    ...
}

// you can also use break and continue statements
```

### Functions

For this language we have function declarations and anonymous functions

```
fn greet(name) {
    ...
}

greet("duck")

let sayname = fn (name){
    ...
}

sayname("duck")

```

### Builtins

We also have built in functions such as:

```
prinltn(...) // prints to the terminal
input(...) // collects input from the terminal
time() // returns the current time in a number datatype

to_number(...) // turns a valid value into a number value
to_boolean(...) // turns a valid value into a boolean value
to_string(...) // turns a valid value into a string

len(...) // returns the length of a string and array
format(...) // example > format ("Hello {}!", "duck") < returns the formatted value
append(...) // appends a value to an array
type(...) // returns the type of a value
```

### Example program

If i can't write a program in this language then how useful would it be? Let's write a simple program that calculates the square of a number using addition. To calculate the square of a value using purely addition we can use this formula that i came up with myself (at least i think i did): n + 2(n - 1) + 2(n - 2), ... till we reach 0. so if we want to find the square of 4 we can do `4 + 2(3) + 2(2) + 2(1) + 2(0) = 4 + 6 + 4 + 2 + 0 = 16`, so let's implement it in our language

```
fn square(num){
    let result = num

    while num > 0{
        num--

        result += num
    }
    return num
}

square(4) // 16
```