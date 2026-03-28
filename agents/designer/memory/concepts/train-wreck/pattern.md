---
description: Train Wreck anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
graphable: false
---
# Train Wreck

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `a.getB().getC().getD().doThing()` -- long method chains navigating through an object graph
- Multiple dots on a single expression traversing different objects (not fluent API on the same object)
- Violating the Law of Demeter: reaching through multiple layers of objects to get to a distant collaborator
- Null checks chained: `if a and a.b and a.b.c and a.b.c.d`
- Code that breaks when any intermediate object in the chain changes its structure

### Confidence

- **high** -- a single expression chains through 4+ different objects' methods or properties to reach a value
- **medium** -- code reaches through 2-3 objects and would break if any intermediate type changed
- **low** -- a fluent API chain on the same builder object (this is intentional and not a train wreck)

## Impact

Tight coupling to the entire object structure, making the code fragile to any change in the intermediate types.

### Symptoms

- A change to one class deep in the hierarchy breaks code in distant, seemingly unrelated modules
- NullPointerException or AttributeError at some point in the chain with no clear indication of which link was null
- Test setup requires building elaborate object graphs just to reach the value the test needs
- Code duplication: the same chain appears in multiple places because there is no encapsulated accessor
- Refactoring any intermediate class requires updating every chain that traverses through it

### Remediation

- Follow the Law of Demeter: only talk to your immediate collaborators, not their collaborators
- Create delegate methods that encapsulate the traversal: `a.doThingOnD()` instead of `a.getB().getC().getD().doThing()`
- Pass the needed value directly rather than passing the root object and letting the callee navigate
- Use null-safe navigation operators (`?.` in Kotlin/C#, `&.` in Ruby) as a stopgap, not a solution
- Flatten the data structure if the deep nesting does not represent a genuine domain relationship
