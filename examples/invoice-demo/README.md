# Synthetic invoice fixture

This tiny service is an intentionally imperfect evaluation target. All records
are fictional. An authenticated customer should only be able to read their own
invoice. The owner must retain access and anonymous requests must be rejected.

It needs only Python's standard library and has no network service or dependencies.
