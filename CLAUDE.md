# CellBlender — guidance for Claude

## Always update the CellBlender ID before committing

Before creating any commit that will be pushed, run:

```
python3 update_cellblender_id.py
```

and include the resulting `cellblender_id.py` change in the same commit
(amend if the commit was already made). The ID is a SHA over the source
files; it is used by CellBlender to detect when a model was saved with a
different version and to offer upgrades. Forgetting to refresh it means
installed CellBlenders won't recognize the new version.

The script is a no-op if nothing changed, so it's safe to always run it.
