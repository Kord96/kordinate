---
kind: concept
name: active-record
signatures:
  concept: active-record
  positive:
    strong:
    - ORM model classes with save or delete behavior on the entity itself
    - model classes inheriting from framework persistence base classes
    medium:
    - query helpers and validations attached directly to model classes
    weak:
    - plain data models with a few persistence-like helpers
  negative:
  - repositories or data mappers isolate all persistence from the model
  - domain entities remain plain objects with no persistence APIs
  notes:
  - Distinguish this from data-mapper; Active Record mixes domain data and persistence.
type: pattern
abstraction:
- design
- data
scope: backend
status: primary
review_questions:
  threshold: 5
  entries:
  - id: active-record-persistence-on-model
    prompt: Do model instances or model classes directly own persistence methods such
      as save, update, create, or query?
    weight: 3
    signals:
    - models.Model
    - ActiveRecord::Base
    - .save(
  - id: active-record-domain-and-storage-mixed
    prompt: Are domain rules and persistence behavior intentionally combined in the
      same model object rather than split behind repositories or mappers?
    weight: 2
    signals:
    - objects.filter
    - belongs_to
    - has_many
monitoring:
  applies_to:
  - component
  - state
  health_signals: []
  business_metrics: []
  gaps:
  - Active Record is primarily a code-structure concept; monitor the persistence operations
    rather than the concept itself.
family: design-patterns
---

# Explanation

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

### Confidence

- **high** -- model instances call `self.save()` and class methods query the database directly
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

### Relationship To Other Concepts

- Related to [repository](/concepts/repository) because active record systems are often contrasted with repository-based domain access layers.
- Related to [data-mapper](/concepts/data-mapper) as the main alternative persistence style where domain objects do not own their own persistence logic.
- Usually prefer this over [data-mapper](/concepts/data-mapper) only when model objects themselves clearly expose persistence behavior and query APIs.

### Boundary

Use `active-record` when model objects themselves encapsulate both domain state and persistence operations.

Do not use it for any ORM model class. The important signal is that the record object itself is the main persistence boundary rather than being mapped by a separate layer.
