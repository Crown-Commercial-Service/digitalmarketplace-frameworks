# Digital Marketplace frameworks changelog

Records breaking changes from major version bumps

## 11.0.0

Removed the transformation of the status field entirely. The DOS search filters
now use the `statusOpenClosed` field for filtering.

Add the `statusOpenClosed` field to DOS3 mappings as well.

## 10.0.0

The `search_filters.yml` manifest has been renamed to `<doc type>_search_filters.yml`. Code which referenced a
`search_filters.yml` prevously should probably now reference `services_search_filters.yml`.

Also changes the mapping json `_meta` key `dmSortClause` to `dm_sort_clause` which it was supposed to be all along except
the wrong version got merged (oops).

## 9.0.0

Upgraded the services mapping for G-Cloud 9 (and implicitly future iterations) to be compatible with Elasticsearch 5.x.
This new mapping is incompatible with Elasticsearch 1.x, so any search-api instances using this version of the
frameworks repository need to be deployed with an ES5 backend.

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
