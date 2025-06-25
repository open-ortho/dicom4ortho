# General Coding Specifications

Specs to use as context for LLMs when coding: copy into projects `docs/specifications` or similar folder, then remove this line.

## 1\. **Meaningful Names**

- Use descriptive and unambiguous names for variables, functions, and classes.
- Avoid generic names; names should reveal intention.

## 2\. **Functions Should Be Small and Do One Thing**

- Keep functions short and focused on a single responsibility.
- Avoid side effects and ensure each function does exactly what its name implies.

## 3\. **Use Comments Wisely**

- Code should be self-explanatory; use comments to explain _why_ something is done, not _what_ is done.
- Remove obsolete or misleading comments.
- When you add a component (function, method, class, module,...) document why you added it, what was it's initial purpose, to determine if you can change it or remove it in the future.

## 4\. **Necessary Code Only**

- Only write code if you use it: don't add any extra functions, classes or code.
- Remove code that is not used.


## 5\. **Objects and Data Structures**

- Hide implementation details; expose only what is necessary.
- Prefer data objects for data, and service objects for behavior.

## 6\. **Error Handling**

- Use exceptions rather than error codes.
- Handle errors at the appropriate level of abstraction.
- Don't return null, and avoid passing null.

## 7\. **DRY: Don't Repeat Yourself**

- Avoid code duplication.
- Extract common code into functions or classes.

## 8\. **Single Responsibility Principle (SRP)**

- Each class or module should have one and only one reason to change.

## 9\. **Open/Closed Principle**

- Classes should be open for extension but closed for modification.

## 10\. **Test-Driven Development (TDD)**

- Write automated tests.
- Tests should be fast, independent, and repeatable.

## 11\. **Continuous Refactoring**

- Refactor code regularly to improve structure without changing behavior.
- Eliminate code smells and keep code clean over time.

## 12\. **Readable Code is Prioritized**

- Prioritize code readability over cleverness or optimization.
- Clean code is easy to read, understand, and maintain.
