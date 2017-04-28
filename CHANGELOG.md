# Digital Marketplace frameworks changelog

Records breaking changes from major version bumps

## 8.0.0 (equivalent to 7.1.0)

Applies a 'datetodatetimeformat' filter to some of the content in DOS2, which requires updated content-loader and dmutils.

To pull this into the frontend apps, manually update requirements for dmutils >= 25.1.0, content-loader >= 4.2.0

## 7.0.0

PR: [#413](https://github.com/alphagov/digitalmarketplace-frameworks/pull/413)

###

New `date` field type. Creation and implementation.

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
