# Digital Marketplace frameworks changelog

Records breaking changes from major version bumps

## 18.0.0

The search mappings G-Cloud 12 and DOS4/5 and the search scheme generator will now
work with Elasticsearch 7, but will no longer work with Elasticsearch 6.

## 17.0.0

Removes the customer benefits record email from G-Cloud 11 manifest, as this is no longer used by CCS. This was only
used in the G-Cloud Direct Award flow in the Buyer Frontend.

## 16.0.0

Removes the Documents section from the `display_service` G-Cloud 10 and G-Cloud 11 manifests. This will be replaced
by a separate document template in the Buyer FE, allowing a combination of service documents and declaration documents.

## 15.0.0

Removed the `include_in_all` parameter from the `serviceIdHash` field in the
search mappings, as `_all` has been deprecated in Elasticsearch 5.6 and will be
removed in Elasticsearch 6. Consumers of the Elasticsearch search mappings will
now need to ensure that searches do not include the `serviceIdHash` field to
remain compliant.

## 14.0.0

Updated the `generate-validation-schemas` and `generate-assessment-schemas` scripts. These scripts now reflect the fact
that we use JSON Draft 07 standard. The backwards incompatible change is that `exclusiveMaximum` is now an integer.
Where we used both `exclusiveMaximum` and `maximum`, I've removed `maximum` in favour of solely using `exclusiveMaximum`
to reduce the repetition. `maximum` by itself now signifies an inclusive maximum.
 
## 13.0.0

Removed buyers guide links from the frameworks, as they are no longer framework-specific. The guide is tied
to the direct award process as implemented for any G-Cloud-like framework on the Digital Marketplace.

## 12.0.0

All the `messages/dates.yml` files for frameworks have been removed. These dates are now stored directly on the
`framework` record in the API as datetimestamps. Any frontends that load `dates.yml` files will need to instead
look for dates in the framework record(s).

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
