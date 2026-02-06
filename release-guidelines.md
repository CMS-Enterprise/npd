# NPD Release Guidelines

NPD will see regular updates and new releases. This document describes the general guidelines around how and when a new release is cut.

## Table of Contents

- [Versioning](#versioning)
  <!-- * [Breaking vs. non-breaking changes](#breaking-vs-non-breaking-changes) -->
  - [Ongoing version support](#ongoing-version-support)
- [Release Process](#release-process)
  - [Goals](#goals)
  - [Schedule](#schedule)
  - [Communication and Workflow](#communication-and-workflow)
  <!-- * [Beta Features](#beta-features) -->
- [Preparing a Release Candidate](#preparing-a-release-candidate)
- [Making a Release](#making-a-release)
- [Auto Changelog](#auto-changelog)
- [Hotfix Releases](#hotfix-releases)

## Versioning

NPD uses Semantic Versioning. Each release is associated with a [git tag](github.com/CMS-Enterprise/NPD/tags) of the form X.Y.Z.

Given a version number in the MAJOR.MINOR.PATCH (eg., X.Y.Z) format, here are the differences in these terms:

    MAJOR version - make breaking/incompatible API changes
    MINOR version - add functionality in a backwards compatible manner
    PATCH version - make backwards compatible bug fixes


<!-- ### Breaking vs. non-breaking changes -->

<!--- TODO: Examples and protocol for breaking changes

Definitions for breaking changes will vary depending on the use-case and project but generally speaking if changes break standard workflows in any way then they should be put in a major version update.
-->

### Ongoing version support

At this time this project will support the latest release of NPD. The release branch will be maintained and kept stable, hotfixes will be prepared in the event that the release branch breaks. 

<!-- TODO: List of supported releases

This section should make clear which versions of the project are considered actively supported.
-->

## Release Process

The sections below define the release process itself, including timeline, roles, and communication best practices.

### Goals

<!-- TODO: Explain the goals of your project’s release structure

This should ideally be a bulleted list of what your regular releases will deliver to key users and stakeholders
-->

NPD has a release process that prioritizes the stability of production releases while maintaining developer flexibility. 

Regular releases of NPD will be made from the `release` branch which will be merged into from the `main` branch. The release branch will be tested in the `prod-test` environment before a new release is tagged from the `release` branch. 

Feature branches will be merged into `main` and be tested in the `dev` environment. Feature branches will be short lived and correspond directly to a ticket. 

### Schedule

As of now, NPD cuts releases as needed on a non-regular schedule. 

### Communication and Workflow

To be notified about releases, we have our releases page on GitHub. To get involved further and potentially get added to more meetings and working groups [shoot us an email at opensource@cms.hhs.gov](mailto:opensource@cms.hhs.gov).

For comments or concerns about the tool or releases you can [file an issue on our GitHub repository](https://github.com/CMS-Enterprise/npd/issues). 

<!-- TODO: (OPTIONAL) Support beta feature testing
## Beta Features

When a new beta feature is created for a release, make sure to create a new Issue with a '[Feature Name] - Beta [X.X.x] - Feedback' title and a 'beta' label. Update the spec text for the beta feature with 'Beta feature: Yes (as of X.X.x). Leave feedback' with a link to the new feature Issue.

Once an item is moved out of beta, close its Issue and change the text to say 'Beta feature: No (as of X.X.x)'.
-->

## Preparing a Release Candidate

The following steps outline the process to prepare a Release Candidate of NPD. This process makes public the intention and contents of an upcoming release, while allowing work on the next release to continue as usual in `main`.

1. Create a Pull Request from the tip of `main` named into the `release` branch. This branch will be used to prepare the Release Candidate. Undergo revisions if needed.

2. Deploy the release candidate to prod-test server. Carefully validate through automated and manual checks.

3. Create a tag like `x.y.z` for this Release. For example, for the first `0.5.0` Release Candidate:

   ```bash
   git fetch
   git checkout origin/release
   git tag 0.5.0
   git push --tags
   ```
  
  Tagged releases are not automatically deployed to production.

## Making a Release

The following steps describe how to make an approved [Release Candidate](#preparing-a-release-candidate) an official release of NPD:

1. **Approved**. Ensure review has been completed and approval granted.

3. **Main**. Open a Pull Request from the release branch to `main`. Merge this PR to ensure any changes to the Release Candidate during the review process make their way back into `main`.

4. **Release**. Publish a [Release in GitHub](proj-releases-new) with the following information

   - Tag version: [X.Y.Z] (note this will create the tag for the `release` branch code when you publish the release)
   - Target: release
   - Release title: [X.Y.Z]
   - Description: copy in Release Notes created earlier
   - This is a pre-release: DO NOT check

5. **Branch**. Finally, keep the release branch and don't delete it. This allows easy access to a browsable spec.

## Auto Changelog

It is recommended to use the provided auto changelog github workflow to populate the project’s CHANGELOG.md file:

```yml
name: Changelog
on:
  release:
    types:
      - created
jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - name: "Auto Generate changelog"
        uses: heinrichreimer/action-github-changelog-generator@v2.3
        with:
          token: ${{{{ secrets.GITHUB_TOKEN }}}}
```

This provided workflow will automatically populate the CHANGELOG.md with all of the associated changes created since the last release that are included in the current release.

This workflow will be triggered when a new release is created.

If you do not wish to use automatic changelogs, you can delete the workflow and update the CHANGELOG.md file manually. Although, this is not recommended.

For best practices on writing changelogs, see: https://keepachangelog.com/en/1.1.0/#how

## Hotfix Releases

If a production issue is identified that requires a quick turnaround, we follow a hotfix process. Rather than creating a feature branch from `main`, the responding engineer creates a `hotfix` branch from `release`. Hotfix branches follow this naming scheme:

```
<contributor>/hotfix-<ticket-number?>-<description-of-the-work>
```

After completing work, the developer opens pull requests against `release` and `main`

1. Create hotfix branch from release

2. PR from branch into `release`

3. Merge PR

4. Tag release with prod-hotfix-version to prod:

   ```bash
   git fetch
   git checkout release
   git tag <prod-hotfix-version>
   git push --tags
   ```

4. Create a [GitHub Release](proj-releases-new) from this tag and the support branch. For example if `0.3.3` is the new hotfix version:

   ```md
   Tag version: 0.3.3
   Target: 0.3.x
   Release title: 0.3.3
   Description: [copy in ReleaseNotes created earlier]
   This is a pre-release: DO NOT check
   ```

[proj-releases-new]: https://github.com/CMS-Enterprise/NPD/releases/new

[Inspiration for this document](https://github.com/openmobilityfoundation/governance/blob/main/technical/ReleaseGuidelines.md)
