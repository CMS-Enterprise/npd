# Localization

The NPD API documentation supports internationalization via Django's translation framework. All API documentation strings in `documentation_content.py` are wrapped in `gettext_lazy` so they are translation ready.

Currently, only English is supported. No additional setup is required until we decide to add a new language.

## Adding a New Language

1. **Register the language** in `settings.py`:

```python
LANGUAGES = [
    ("en", _("English")),
    ("es", _("Spanish")),  # add new language here
]
```

2. **Generate translation files**:

```bash
python manage.py makemessages -l es
```

This scans all `_()` calls and creates `locale/es/LC_MESSAGES/django.po`.

3. **Translate the strings** in the generated `.po` file. Each entry has a `msgid` which is the original English string and a `msgstr` where the translation goes.

4. **Compile translations**:

```bash
python manage.py compilemessages
```

This produces `.mo` binary files that Django reads at runtime.


## File Structure

```
locale/
└── es/
    └── LC_MESSAGES/
        ├── django.po    # human-editable translations
        └── django.mo    # compiled binary (generated, do not edit)
```

**NOTE:** We should add `*.mo` to `.gitignore` and integrate `compilemessages` as part of our build/deploy process. `makemessages` must be a manual step done by the developer so it can be ready for compilation.