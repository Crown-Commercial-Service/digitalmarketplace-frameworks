# Digital Marketplace frameworks changelog

Records breaking changes from major version bumps

## 6.0.0

PR: [#381](https://github.com/alphagov/digitalmarketplace-frameworks/pull/381)

### What changed

New `followup` key structure requires digitalmarketplace-content-loader@3.0.0

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
