# Recursive Functions in Lisp

### Recursive Definitions in Lisp

Recursive definitions are procedures that call themselves either directly or indirectly to solve a problem. In programming, recursion is a powerful tool for tasks that can be broken down into simpler, smaller tasks of the same type. Here’s how recursion works, illustrated through the example of calculating the square root:

1. **Base Case**: This is the simplest instance of the problem, which can be solved directly without further recursion. For example, if the guess is good enough (close enough to the actual square root), the recursion ends.

2. **Recursive Case**: This is where the function calls itself with modified parameters, aiming to reach the base case eventually. For finding the square root, if the guess is not good enough, the function refines the guess and calls itself again.

The following is a simplified example of a recursive definition for calculating the square root algorithmically in Lisp:

```lisp
(define (good-enough? guess x)
  (< (abs (- (* guess guess) x)) 0.0001))

(define (improve guess x)
  (/ (+ guess (/ x guess)) 2))

(define (try guess x)
  (if (good-enough? guess x) 
      guess 
      (try (improve guess x) x)))

(define (square-root x)
  (try 1.0 x)) ; Start trying with an initial guess of 1.0
```

In this definition:
- `good-enough?` checks if the square of the guess is sufficiently close to `x`.
- `improve` computes the new guess.
- `try` is the recursive function that attempts to find the square root by refining the guess until `good-enough?` returns true.

### Installing Lisp

To begin programming in Lisp, you’ll need to install a Lisp interpreter. One of the popular choices is **SBCL (Steel Bank Common Lisp)**. Here’s how to get started with it based on your operating system:

#### For macOS:
1. **Using Homebrew**:
   - Open the Terminal.
   - Run the command: 
     ```bash
     brew install sbcl
     ```

#### For Windows:
1. **Using Chocolatey**:
   - Open Command Prompt as Administrator.
   - Run the command:
     ```bash
     choco install sbcl
     ```

2. **Manual Installation**:
   - Download the SBCL installer from the [SBCL website](http://www.sbcl.org/platform/index.html).
   - Follow the installation instructions on the website.

#### For Linux:
1. **Using APT (Debian/Ubuntu)**:
   - Open the Terminal.
   - Run the command:
     ```bash
     sudo apt install sbcl
     ```

2. **Other Distributions**: Check your package manager or download from the SBCL website.

### Writing a Very Simple Program in Lisp

Once you have SBCL installed, you can write a simple program. Let’s create a program that calculates the factorial of a number using recursion:

1. **Open the SBCL REPL**:
   - Run the command `sbcl` in your terminal.

2. **Input the following program**:

```lisp
(define (factorial n)
  (if (<= n 1)             ; Base case: if n is 1 or less
      1                    ; return 1
      (* n (factorial (- n 1))))) ; Recursive case
```

3. **Test the function**:
   - To calculate the factorial of 5, type:
   ```lisp
   (factorial 5)
   ```
   - The expected output should be `120`.

### Summary

- Recursive definitions are a foundation of effective problem-solving in programming, where problems can be broken down into simpler sub-problems.
- You can install a Lisp interpreter like SBCL and run simple programs to practice recursion and other features of the language.

If you have any more specific questions or need further assistance, feel free to ask!

---

[Link to Video](https://www.youtube.com/watch?v=2Op3QLzMgSY)