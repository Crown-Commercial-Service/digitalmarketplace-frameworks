Digital Marketplace content
================================================================================
YAML definitions of the Digital Marketplace’s procurement frameworks.

Running the tests
--------------------------------------------------------------------------------
The tests check that the YAML files are valid and that they match a schema.

Setup a VirtualEnv
`mkvirtualenv`

Install dependencies
`pip install -r requirements_for_test.txt`

Run the tests
`py.test`

Versioning
--------------------------------------------------------------------------------
Releases of this project follow [semantic versioning](http://semver.org/), ie
> Given a version number MAJOR.MINOR.PATCH, increment the:
>
> - MAJOR version when you make incompatible API changes,
> - MINOR version when you add functionality in a backwards-compatible manner, and
> - PATCH version when you make backwards-compatible bug fixes.

To make a new version:
- update `VERSION.txt` with the new version number
- commit this change; the first line of the commit message **must** be in the
  format `Bump version to X.X.X`
- create a pull request for the version bump

When the pull request is merged a Jenkins job will be run to tag the new
version.
