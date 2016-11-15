# Digital Marketplace frameworks changelog

Records breaking changes from major version bumps

## 5.0.0

PR: [#330](https://github.com/alphagov/digitalmarketplace-frameworks/pull/330)

### What changed

We rename the `edit_brief_response` manifest to`legacy_edit_brief_response`.

### Example app change

Old
```
content_loader.get_manifest('digital-outcomes-and-specialists', 'edit_brief_response')
```

New
```
content_loader.get_manifest('digital-outcomes-and-specialists', 'legacy_edit_brief_response')
```