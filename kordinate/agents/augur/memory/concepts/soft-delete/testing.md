---
description: Soft Delete — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test that default query scopes exclude soft-deleted records without any explicit filter
- Verify that explicit queries can retrieve soft-deleted records when needed (admin, audit, restore)
- Test unique constraint behavior: re-creating a record with the same natural key as a soft-deleted one
- Test cascading soft delete: deleting a parent soft-deletes all children consistently
- Verify the restore/undelete operation correctly reinstates the record and its relationships
- Test the purge job: records past the retention period are hard-deleted and no longer accessible
- Assert that foreign key relationships handle soft-deleted parents correctly (no orphaned active children)
