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
    - [Dependencies](#dependencies)
    - [Installing](#installing)
    - [Building the Project](#building-the-project)
      - [Database Setup](#database-setup)
      - [Running the Application](#running-the-application)
      - [One-off commands](#one-off-commands)
    - [Troubleshooting](#troubleshooting)
      - [1. PostgreSQL collation version mismatch](#1-postgresql-collation-version-mismatch)
      - [2. Docker volume image mismatch](#2-docker-volume-image-mismatch)
      - [3. Port already in use](#3-port-already-in-use)
      - [4. Updated elements do not appear on the frontend after build](#4-updated-elements-do-not-appear-on-the-frontend-after-build)
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

### Dependencies
The following tools **must be installed on your machine** before running any project commands, but it is important to note that some of these may be installed on your machine by default:

- Python 3.10 or later
- Docker
- Docker Compose  
- GNU Make  

### Installing

Python and Javascript dependencies are handled via docker containers, so they
will be built when running `docker compose build` or when running `docker
compose up` for the first time. The above installations are needed for local testing.

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

### Troubleshooting
#### 1. PostgreSQL collation version mismatch

**Error**
```
ERROR: template database "template1" has a collation version mismatch
```

**Cause**
```
A PostgreSQL Docker volume was created using a different system library version
```
**Fix**
This should automatically be resolved by the Flyway migration `R__refresh_collation_version.sql`.
However, if the migration fails to resolve the issue, fall back to recreating the volume:

```
docker compose down -v
make setup
```
⚠️ _This deletes local development database data_

#### 2. Docker volume image mismatch 

**Error**
```
ERROR: extension "postgis" already exists
```

**Cause**
```
Mismatch of Docker database images due to deprecated older code or a partially completed migration
```
**Fix**
```
make reset-db
make setup
```

#### 3. Port already in use

**Error**
```
bind: address already in use
```

**Cause**
```
Another local service is already using a required port
```
**Fix**
```
sudo lsof -i :{port}
sudo kill <PID>
```

#### 4. Updated elements do not appear on the frontend after build

**Error**
```
Elements do not appear after either pulling a branch or creating new code
```

**Cause**
```
Cached frontend assets or stale build artifacts are being served by the browser or container
```
**Fix**
```
CMD + Shift + R
make clean-frontend
make build-frontend-assets
```

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

Please refer to our [Release Guidelines](release-guidelines.md) to read how we make releases.

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
