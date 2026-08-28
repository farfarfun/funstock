# Changelog

## Unreleased

### Breaking

- Renamed the source package / import name / PyPI distribution name from
  `notestock` to `funstock` to match the GitHub repository name (already
  renamed from `notestock` to `funstock` previously). Update any code using
  `import notestock` / `from notestock...` to `import funstock` / `from
  funstock...`.
  - `notestock` was never actually published to PyPI (confirmed 404), so
    there is no old-package forwarding release needed — this is a clean
    rename with no compatibility shim.
  - Part of farfarfun/todo-list#299.
