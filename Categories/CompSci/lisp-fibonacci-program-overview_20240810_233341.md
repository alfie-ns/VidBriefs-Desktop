# Lisp Fibonacci Program Overview

Certainly! Below is a well-structured and substantial Lisp program that demonstrates various concepts such as recursion, higher-order procedures, and abstraction. This program calculates the Fibonacci sequence and leverages the concepts discussed in our conversation.

### Fibonacci Sequence Program in Lisp

The Fibonacci sequence is defined as follows:
- \( F(0) = 0 \)
- \( F(1) = 1 \)
- \( F(n) = F(n - 1) + F(n - 2) \) for \( n > 1 \)

This program also includes an efficient implementation using memoization, which stores the results of expensive function calls and returns the cached results when the same inputs occur again.

```lisp
; Define a function to compute the nth Fibonacci number using recursion.
(define (fibonacci n)
  (if (< n 2)
      n ; Base cases: 0 and 1
      (+ (fibonacci (- n 1)) (fibonacci (- n 2))))) ; Recursive cases

; Define a memoization helper function to improve performance.
(define (make-memoized-fibonacci)
  (define cache (make-table)) ; Create a cache table
  (define (fib n)
    (if (table-contains? cache n) ; Check if the result is cached
        (table-get cache n)       ; Return cached result
        (let ((result (fibonacci n))) ; Compute Fibonacci
          (table-set! cache n result) ; Store the result in cache
          result))) ; Return the result
  fib) ; Return the memoized function

; Define a simple table structure to hold cached Fibonacci results.
(define (make-table)
  (define table (make-vector 100)) ; Create a fixed-size vector
  (define (get n) (vector-ref table n)) ; Get value from table
  (define (set! n value) (vector-set! table n value)) ; Set value in table
  (define (contains? n) (not (eq? (vector-ref table n) #f))) ; Check if value exists
  (define (initialize) (do ((i 0 (+ i 1))) ((= i (vector-length table))) (vector-set! table i #f))) ; Initialize table with #f
  (initialize)
  (list get set! contains?)) ; Return get, set!, and contains? functions

; Create a new memoized Fibonacci function.
(define memoized-fib (make-memoized-fibonacci))

; Example usage:
(display "Fibonacci of 10: ")
(display (memoized-fib 10)) ; Calculate Fibonacci of 10
(newline)

(display "Fibonacci of 20: ")
(display (memoized-fib 20)) ; Calculate Fibonacci of 20
(newline)

(display "Fibonacci of 30: ")
(display (memoized-fib 30)) ; Calculate Fibonacci of 30
(newline)
```

### Explanation of Key Components

1. **Basic Recursive Function**: The `fibonacci` function calculates Fibonacci numbers using a simple base case for \(0\) and \(1\) and the recursive relationship for other values.

2. **Memoization**: The `make-memoized-fibonacci` function creates an environment that caches results of previously computed Fibonacci numbers to optimize further calls. It uses a simple fixed-size cache implemented with a vector.

3. **Table Management**: 
   - `make-table` initializes a vector that acts as a cache. It provides functions `get`, `set!`, and `contains?` to manage the cache efficiently.

4. **Usage**: At the end of the program, we see examples of how to display the Fibonacci numbers for \(10\), \(20\), and \(30\).

### Installing and Running the Program

1. **Installation**:
   Follow the instructions mentioned earlier to install SBCL or your chosen Lisp environment.

2. **Running the Program**:
   - Save the above Lisp code to a file named `fibonacci.lisp`.
   - Start the SBCL REPL (Run `sbcl` in your terminal).
   - Load your file by using the command:
     ```lisp
     (load "path/to/fibonacci.lisp")
     ```
   - The program should output the Fibonacci numbers for \(10\), \(20\), and \(30\).

### Note
This program illustrates how you can use recursion and higher-order functions effectively in Lisp to tackle a familiar computational problem. If you have additional questions or need further exploration on any specific aspects of the program, feel free to ask!

---

[Link to Video](https://www.youtube.com/watch?v=2Op3QLzMgSY)