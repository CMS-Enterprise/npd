| Status  | Date       | Author         | Context                                       |
| ------- | ---------- | -------------- | --------------------------------------------- |
| Drafted | 2029-07-01 | @spopelka-dsac | project scaffolding                           |
| Updated | 2029-08-19 | @spopelka-dsac | adding data and docker notes                  |
| Updated | 2029-09-30 | @abachman-dsac | clarification of coding styles and PR details |
| Updated | 2029-10-15 | @abachman-dsac | addressing feedback from #108                 |
| Updated | 2029-12-03 | @abachman-dsac | adding notes on `make` and `bin/npr`          |
| Updated | 2026-01-28 | @sachin-panayil| updating links with new path                  |

- [How to Contribute](#how-to-contribute)
  - [Getting Started](#getting-started)
    - [Team Specific Guidelines](#team-specific-guidelines)
    - [Installing](#installing)
    - [Building the Project](#building-the-project)
      - [Database Setup](#database-setup)
      - [Running the Application](#running-the-application)
      - [One-off commands](#one-off-commands)
    - [Workflow and Branching](#workflow-and-branching)
    - [Testing Conventions](#testing-conventions)
      - [Backend Tests](#backend-tests)
    - [Coding Style and Linters](#coding-style-and-linters)
    - [Writing Issues](#writing-issues)
    - [Creating Commits](#creating-commits)
      - [Commit Messages](#commit-messages)
      - [Pull Request Descriptions](#pull-request-descriptions)
  - [Reviewing Pull Requests](#reviewing-pull-requests)
  - [Shipping Releases](#shipping-releases)
  - [Documentation](#documentation)
  - [Policies](#policies)
    - [Open Source Policy](#open-source-policy)
    - [Security and Responsible Disclosure Policy](#security-and-responsible-disclosure-policy)
  - [Public domain](#public-domain)

# How to Contribute

<!-- Basic instructions about where to send patches, check out source code, and get development support.-->

We're so thankful you're considering contributing to an [open source project of
the U.S. government](https://code.gov/)! If you're unsure about anything, just
ask -- or submit the issue or pull request anyway. The worst that can happen is
you'll be politely asked to change something. We appreciate all friendly
contributions.

We encourage you to read this project's CONTRIBUTING policy (you are here), its
[LICENSE](LICENSE.md), and its [README](README.md).

These instructions are general and do not cover every scenario. [Create an
issue](https://github.com/CMS-Enterprise/npd/issues) on this project or double check
current documentation if you run into a situation you are unable to solve by
rebuilding the application from scratch.

## Getting Started

### Team Specific Guidelines

While being fully developed in the open, this project is a hybrid project
largely staffed by members of the [DSAC](https://www.cms.gov/digital-service)
team, but not restricted to CMS team members. We welcome
[issues](https://github.com/CMS-Enterprise/npd/issues) and
[contributions](https://github.com/CMS-Enterprise/npd/pulls) from the open source and
health-tech community at large.

The team uses an internal Jira instance for planning and tracking work but
seeks to hold any discussions relevant to specific Pull Requests in the open.

### Installing

Python and Javascript dependencies are handled via docker containers, so they
will be built when running `docker compose build` or when running `docker
compose up` for the first time.

Local dependencies for project tooling and testing can be installed with `make`:

```sh
# build containers, create and migrate the development database
make setup

# install ruff and playwright
make install-tools
```

If you prefer to run on host (aka, not inside docker containers), you will have
to follow the instructions provided by your language tooling for installing
dependencies locally. We recommend using `pip` in the `backend/` directory for Python and `npm` in the `frontend/` and `playwright/` directories for Javascript.

### Building the Project

The NPD application is a Django application located in the
`backend/` sub-directory, serving a React single-page application which is located in the `frontend/` sub-directory, with data provided by a database whose schema is managed by [flyway](https://documentation.red-gate.com/fd/getting-started-with-flyway-184127223.html) using SQL source code from the `flyway/` directory.

All commands listed below assume you are at the root of the project in your shell.

#### Database Setup

Running `make setup` will:

- start the development database service
- create the default development database
- migrate the development data base to the current version

#### Running the Application

To start the development project with system defaults, run `make setup` and then `make up`.

You can sign in to the application using the default development user account at http://localhost:8000/accounts/login/ with username: ` developer@cms.hhs.gov`, password: `password123`. You can use the same credentials to sign in to the Django admin site at http://localhost:8000/admin/login/.

_Optional_: you can manage your local project environment variables by creating a "dotenv" file in the `backend/` directory. The easiest way to do that is make a copy of the example:

```sh
cp backend/.env_template backend/.env
```

#### One-off commands

We recommend use of [Docker Compose](https://docs.docker.com/compose/), `make`, and the `bin/npr` tool included in this project for all development work.

You can review the use of those tools by running `make` or `bin/npr --help` at the command line.

`make` is intended to provide the most common commands in a standard shape for development work.

`bin/npr` is a runner for managing complex `docker compose run` commands across the various services that make up this project.

### Workflow and Branching

We follow the [GitHub Flow Workflow](https://guides.github.com/introduction/flow/).

1.  Fork the project
2.  Check out the `main` branch
3.  Create a feature branch
4.  Write code and tests for your change
5.  From your branch, make a pull request against `CMS-Enterprise/npd/main`
6.  Work with repo maintainers to get your change reviewed
7.  Wait for your change to be pulled into `CMS-Enterprise/npd/main`
8.  Delete your feature branch

### Testing Conventions

It is an expectation of this project that each feature will have new automated
tests prior to opening a pull request and that all the tests in the repo are
passing.

We do not expect 100% test coverage but we will be unlikely to accept Pull
Requests which reduce test coverage or new features which do not include
updates to the test suite.

We recommend starting new feature work with a new Playwright end-to-end test and going from there.

#### Backend Tests

The backend test suite can be found in the `tests.py` file currently in
`backend/npdfhir/tests.py`. The test suite can be run by navigating to the
`backend` folder and running `make test` or `python manage.py test`.

Please refer to the [Django
documentation](https://docs.djangoproject.com/en/5.2/topics/testing/overview/)
on testing for additional details.

### Coding Style and Linters

We require use of `ruff` to format all Python code and `prettier` to format all Typescript code.

The easiest way to keep your commits clean is to install the formatting tools and pre-commit with `make install-tools`.

### Writing Issues

When creating an issue please try to adhere to the following format:

    module-name: One line summary of the issue (less than 72 characters)

    ### Expected behavior

    As concisely as possible, describe the expected behavior.

    ### Actual behavior

    As concisely as possible, describe the observed behavior.

    ### Steps to reproduce the behavior

    List all relevant steps to reproduce the observed behavior.

    see our .github/ISSUE_TEMPLATE.md for more examples.

In this project, [new issues](https://github.com/CMS-Enterprise/npd/issues) should be
limited to code, development tooling, automation, or site bugs, ___NOT___ data
quality.

### Creating Commits

Files should be exempt of trailing spaces. Tests should pass. Linting should be
clean. Code should be well formatted by tools whenever possible.

We rely on a fairly large set of automated checks in GitHub to maintain code
quality, but you will have a better time if you ensure the checks will pass
before you push.

Assume that "Squash and
Merge"](https://github.blog/open-source/git/squash-your-commits/) will be used
to merge your changes, so don't hesitate to commit early and often in your
branch.


#### Commit Messages

We prefer a specific format for commit messages. Please write your commit
messages along these guidelines. Please keep the line width no greater than 80
columns (You can use `fmt -n -p -w 80` to accomplish this).

Some important notes regarding the first line of your commit message:

* Describe what was done; not the result
* Use the active voice
* Use the present tense
* Capitalize properly
* Do not end in a period — this is a title/subject
* Prefix the subject with its scope

#### Pull Request Descriptions

We prefer

    module-name: One line description of your change (less than 72 characters)

    ## Problem

    <!-- Explain the context and why you're making that change.  What is the problem
    you're trying to solve? In some cases there is not a problem and this can be
    thought of being the motivation for your change. -->

    ## Solution

    <!-- Describe the modifications you've done. -->

    ## Result

    <!-- What will change as a result of your pull request? Note that sometimes this
    section is unnecessary because it is self-explanatory based on the solution. If this
    is a visual change, please include screenshots. -->

    ## Testing / Review

    <!-- What guidance do you have for reviewers with respect to testing and reviewing
    your changes? -->

See our [.github/PULL_REQUEST_TEMPLATE.md](./.github/PULL_REQUEST_TEMPLATE.md) for the current default template.

## Reviewing Pull Requests

In this high velocity development time, we strive for a 24 hour turnaround on
Pull Requests (PRs), but cannot guarantee it.

All PRs will be peer reviewed by one or more CMS team members for code quality,
adherence to existing project standards, and clarity of thought. Code formatting
we would prefer to leave to tools better fit for the job and so we will not
block PRs for formatting issues unless they significantly impact clarity or
functionality.

A PR is required to have 1 approval from a CMS team member on the project before
it can be merged into `main`. Authors may not approve their own work.

After an approval is received, the approver or an author of the PR can use the
"Squash and Merge" feature in GitHub to compress all commits from the branch
into a single commit before merging.

We value communication over authoritative direction. When changes are requested,
it is appropriate to engage in discussion using the communication tools provided
by GitHub to get clarity, explain decisions, etc.

If requested changes are deemed appropriate by both parties, it is expected that
the author themselves make the changes, not the requestor. That is, the author
is responsible for completing the PR while the reviewer--a member of the CMS
team delivering the product who is not the author--is accountable for the
changes being proposed.

<!--- TODO: Make a brief statement about how pull-requests are reviewed, and who is doing the reviewing. Linking to COMMUNITY.md can help.

Code Review Example

The repository on GitHub is kept in sync with an internal repository at
github.cms.gov. For the most part this process should be transparent to the
project users, but it does have some implications for how pull requests are
merged into the codebase.

When you submit a pull request on GitHub, it will be reviewed by the project
community (both inside and outside of github.cms.gov), and once the changes are
approved, your commits will be brought into github.cms.gov's internal system for
additional testing. Once the changes are merged internally, they will be pushed
back to GitHub with the next sync.

This process means that the pull request will not be merged in the usual way.
Instead a member of the project team will post a message in the pull request
thread when your changes have made their way back to GitHub, and the pull
request will be closed.

The changes in the pull request will be collapsed into a single commit, but the
authorship metadata will be preserved.

-->

## Shipping Releases

<!-- TODO: What cadence does your project ship new releases? (e.g. one-time, ad-hoc, periodically, upon merge of new patches) Who does so? Below is a sample template you can use to provide this information.

npd will see regular updates and new releases. This section describes the general guidelines around how and when a new release is cut.

-->

<!-- ### Table of Contents

- [Versioning](#versioning)
  - [Breaking vs. non-breaking changes](#breaking-vs-non-breaking-changes)
  - [Ongoing version support](#ongoing-version-support)
- [Release Process](#release-process)
  - [Goals](#goals)
  - [Schedule](#schedule)
  - [Communication and Workflow](#communication-and-workflow)
  - [Beta Features](#beta-features)
- [Preparing a Release Candidate](#preparing-a-release-candidate)
  - [Incorporating feedback from review](#incorporating-feedback-from-review)
- [Making a Release](#making-a-release)
- [Auto Changelog](#auto-changelog)
- [Hotfix Releases](#hotfix-releases) -->

<!-- ### Versioning

npd uses [Semantic Versioning](https://semver.org/). Each release is associated with a [`git tag`](github.com/CMS-Enterprise/npd/tags) of the form `X.Y.Z`.

Given a version number in the `MAJOR.MINOR.PATCH` (eg., `X.Y.Z`) format, here are the differences in these terms:

- **MAJOR** version - make breaking/incompatible API changes
- **MINOR** version - add functionality in a backwards compatible manner
- **PATCH** version - make backwards compatible bug fixes -->

<!-- ### Breaking vs. non-breaking changes

TODO: Examples and protocol for breaking changes

Definitions for breaking changes will vary depending on the use-case and project but generally speaking if changes break standard workflows in any way then they should be put in a major version update.
-->

<!-- #### Ongoing version support

TODO: Explanation of general thought process

Explain the project’s thought process behind what versions will and won’t be supported in the future.
-->

<!-- TODO: List of supported releases

This section should make clear which versions of the project are considered actively supported.
-->

<!-- ### Release Process

The sections below define the release process itself, including timeline, roles, and communication best practices. -->

<!-- #### Goals

TODO: Explain the goals of your project’s release structure

This should ideally be a bulleted list of what your regular releases will deliver to key users and stakeholders
-->

<!-- #### Schedule

TODO: Communicate the timing of the regular release structure

For example, if you plan on creating regular releases on a weekly basis you should communicate that as well as the typical days upcoming releases will become tagged.

You should also communicate special cases such as security updates or critical bugfixes and how they would likely be released earlier than what is usually scheduled.
-->

<!-- #### Communication and Workflow

TODO: Communicate proper channels to be notified about releases

Communicate the slack channels, mailing lists, or other means of pushing out release notifications.
-->

<!-- TODO: (OPTIONAL) Support beta feature testing
## Beta Features

When a new beta feature is created for a release, make sure to create a new Issue with a '[Feature Name] - Beta [X.X.x] - Feedback' title and a 'beta' label. Update the spec text for the beta feature with 'Beta feature: Yes (as of X.X.x). Leave feedback' with a link to the new feature Issue.

Once an item is moved out of beta, close its Issue and change the text to say 'Beta feature: No (as of X.X.x)'.
-->

<!-- ### Preparing a Release Candidate

The following steps outline the process to prepare a Release Candidate of npd. This process makes public the intention and contents of an upcoming release, while allowing work on the next release to continue as usual in `dev`.

1. Create a _Release branch_ from the tip of `dev` named `release-x.y.z`, where `x.y.z` is the intended version of the release. This branch will be used to prepare the Release Candidate. For example, to prepare a Release Candidate for `0.5.0`:

   ```bash
   git fetch
   git checkout origin/dev
   git checkout -b release-0.5.0
   git push -u origin release-0.5.0
   ```

   Changes generated by the steps below should be committed to this branch later.

2. Create a tag like `x.y.z-rcN` for this Release Candidate. For example, for the first `0.5.0` Release Candidate:

   ```bash
   git fetch
   git checkout origin/release-0.5.0
   git tag 0.5.0-rc1
   git push --tags
   ```

3. Publish a [pre-Release in GitHub](proj-releases-new):

   ```md
   Tag version: [tag you just pushed]
   Target: [release branch]
   Release title: [X.Y.Z Release Candidate N]
   Description: [copy in ReleaseNotes.md created earlier]
   This is a pre-release: Check
   ```

4. Open a Pull Request to `main` from the release branch (eg. `0.5.0-rc1`). This pull request is where review comments and feedback will be collected.

5. Conduct Review of the Pull Request that was opened. -->

<!-- #### Incorporating feedback from review

The review process may result in changes being necessary to the release candidate.

For example, if the second Release Candidate for `0.5.0` is being prepared, after committing necessary changes, create a tag on the tip of the release branch like `0.5.0-rc2` and make a new [GitHub pre-Release](proj-releases-new) from there:

```bash
git fetch
git checkout origin/release-0.5.0
# more commits per OMF review
git tag 0.5.0-rc2
git push --tags
```

Repeat as-needed for subsequent Release Candidates. Note the release branch will be pushed to `dev` at key points in the approval process to ensure the community is working with the latest code. -->

<!-- ### Making a Release

The following steps describe how to make an approved [Release Candidate](#preparing-a-release-candidate) an official release of npd:

1. **Approved**. Ensure review has been completed and approval granted.

2. **Main**. Merge the Pull Request created during the Release Candidate process to `main` to make the release official.

3. **Dev**. Open a Pull Request from the release branch to `dev`. Merge this PR to ensure any changes to the Release Candidate during the review process make their way back into `dev`.

4. **Release**. Publish a [Release in GitHub](proj-releases-new) with the following information

   - Tag version: [X.Y.Z] (note this will create the tag for the `main` branch code when you publish the release)
   - Target: main
   - Release title: [X.Y.Z]
   - Description: copy in Release Notes created earlier
   - This is a pre-release: DO NOT check

5. **Branch**. Finally, keep the release branch and don't delete it. This allows easy access to a browsable spec. -->

<!-- ### Auto Changelog

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
          token: ${{ secrets.GITHUB_TOKEN }}
```

This provided workflow will automatically populate the CHANGELOG.md with all of the associated changes created since the last release that are included in the current release.

This workflow will be triggered when a new release is created.

If you do not wish to use automatic changelogs, you can delete the workflow and update the CHANGELOG.md file manually. Although, this is not recommended.

For best practices on writing changelogs, see: https://keepachangelog.com/en/1.1.0/#how -->

<!-- ### Hotfix Releases

In rare cases, a hotfix for a prior release may be required out-of-phase with the normal release cycle. For example, if a critical bug is discovered in the `0.3.x` line after `0.4.0` has already been released.

1. Create a _Support branch_ from the tag in `main` at which the hotfix is needed. For example if the bug was discovered in `0.3.2`, create a branch from this tag:

   ```bash
   git fetch
   git checkout 0.3.2
   git checkout -b 0.3.x
   git push -u origin 0.3.x
   ```

2. Merge (or commit directly) the hotfix work into this branch.

3. Tag the support branch with the hotfix version. For example if `0.3.2` is the version being hotfixed:

   ```bash
   git fetch
   git checkout 0.3.x
   git tag 0.3.3
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

[proj-releases-new]: https://github.com/CMS-Enterprise/npd/releases/new
-->

## Documentation

We also welcome improvements to the project documentation or to the existing
docs. Please file an [issue](https://github.com/CMS-Enterprise/npd/issues).

## Policies

### Open Source Policy

We adhere to the [CMS Open Source
Policy](https://github.com/CMSGov/cms-open-source-policy). If you have any
questions, just [shoot us an email](mailto:opensource@cms.hhs.gov).

### Security and Responsible Disclosure Policy

_Submit a vulnerability:_ Vulnerability reports can be submitted through [Bugcrowd](https://bugcrowd.com/cms-vdp). Reports may be submitted anonymously. If you share contact information, we will acknowledge receipt of your report within 3 business days.

For more information about our Security, Vulnerability, and Responsible Disclosure Policies, see [SECURITY.md](SECURITY.md).

## Public domain

This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0 dedication. By submitting a pull request or issue, you are agreeing to comply with this waiver of copyright interest.
