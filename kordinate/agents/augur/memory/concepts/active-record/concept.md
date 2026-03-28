---
description: Active Record architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design, data]
---
# Active Record

## Recognition

How to identify this pattern in code.

### Signatures

- Model classes with instance methods `save()`, `delete()`, `update()`
- Class methods like `Model.find()`, `Model.create()`, `Model.where()`
- Models inherit from a base class that provides persistence (e.g., `models.Model`, `ActiveRecord::Base`)
- Django ORM models with `objects.filter()`, `instance.save()`
- Rails ActiveRecord: `belongs_to`, `has_many`, `validates`
- Laravel Eloquent models extending `Model`
- Database columns mapped directly to model attributes

**Not this pattern (Python):** `class Foo(Model)` or `class Foo(db.Model)` in test code, examples, or third-party library extensions does not mean the *project* uses active record as its architecture. Look for active record models in the project's main source code. A library that provides pagination utilities for Django/SQLAlchemy may *reference* models in examples without itself using active record. Similarly, `objects.filter` in test data setup is not evidence of the project's architectural choice.

### Confidence

- **high** -- model instances call `self.save()` and class methods query the database directly, in the project's core source code (not examples/tests)
- **medium** -- ORM models with persistence mixed in but additional service layer present
- **low** -- data classes with a `to_dict()` or `from_row()` that partially resemble active record

## Architecture

Look for model objects that combine domain data and persistence logic in a single class.

### Review Checklist

- Validations are defined on the model and enforced before persistence
- Callbacks/hooks (before_save, after_create) have clear, limited scope
- Query scopes or named queries keep complex lookups readable
- Associations are declared and lazy/eager loading is intentional
- Migrations match the model schema declarations

### Anti-patterns

- Complex business logic embedded in model callbacks (hidden side effects)
- Models with dozens of query scopes that belong in a dedicated query object
- Direct SQL queries that bypass model validations and callbacks
- God models with hundreds of methods mixing persistence, business logic, and presentation
