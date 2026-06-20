# Database Migration Notes

## Current V1.1.1 Behavior

OmniSignal currently creates missing SQLite tables with:

```python
Base.metadata.create_all(bind=engine)
```

This is appropriate for the local-first demo and for adding new tables to a
fresh development database. It is not a general schema migration system:

- It does not alter existing columns.
- It does not rename or backfill fields.
- It does not provide downgrade support.
- It does not coordinate schema versions across multiple application instances.

## V1.1.1 Safety Boundary

The hardening release does not introduce a breaking table alteration. Token
expiry uses the existing `encrypted_tokens.expires_at` column, and reseed
isolation changes application behavior rather than schema shape.

## Production Requirement

Before real multi-user deployment, add Alembic and:

1. Create an initial migration from the SQLAlchemy models.
2. Add an application schema-version check at startup.
3. Back up the local database before migration.
4. Test upgrades with existing encrypted token and real-sync rows.
5. Define downgrade and incident-recovery procedures.

Alembic remains deferred infrastructure work for V1.2/V1.3; `create_all` should
not be treated as sufficient for a hosted production deployment.
