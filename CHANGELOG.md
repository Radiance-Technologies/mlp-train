All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Instructions for developers (adding contributions)
-------------------------------------------
Sort all changes in your merge request (MR) into the following categories:
Added, Changed, Deprecated, Removed, Fixed, and Security.
For each category X into which your changes are sorted, ensure a
"#### X" subheading exists in the Unreleased/Prerelease section.
Add your changes to their respective categories' sections as a bulleted
list, prepending to any previously existing list.
Place ONE empty line between the section header and your bullet.
Place TWO empty lines between each bullet to reduce the risk of
merge conflicts.
Ensure each change includes a cross-reference to the MR that introduced it.
For example, if merge request 12 added a class C and function F, removed
a method M from class D, and fixed a bug in function B, then we could expect
something like the following Prerelease section (where prior MRs are presumed
to have already contributed):

```
### Prerelease

#### Added

- [!12] Added class `C`


- [!12] Added function `F`


- [!11] Added ...


- [!7] Added ...


#### Deprecated


- [!10] Feature `Y` is deprecated and will be removed in version xx.yy.zz.
Use `Z` instead.

#### Removed


- [!12] Removed `D.M`


- [!8] Removed ...

#### Fixed


- [!12] Fixed bug in `B`
```
-->


## [Unreleased]

### Planned

### Prerelease

#### Added

#### Changed

#### Removed

<!--
Instructions for maintainers (preparing releases)
---------------------------------------
Move the Added, Changed, Deprecated, Removed, Fixed, and Security sections in
the Unreleased/Prerelease section to a new section in the following format:

```
## [X.Y.Z] YYYY-MM-DD
### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security
```

where X.Y.Z are the major, minor, and patch version numbers (chosen according to
the package versioning policy), and YYYY-MM-DD is the current date.
Retain the empty "### Prerelease" section.
Create a tag `X.Y.Z` and push it to Gitlab.
The `release` stage of the CI/CD pipeline will run for the resulting tag
and publish/deploy the new version of the package.
-->

<!-- ## [X.Y.Z] YYYY-MM-DD
### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security -->
