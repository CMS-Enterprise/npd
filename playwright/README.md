- [Local setup](#local-setup)
- [Running tests](#running-tests)
  - [Locally](#locally)
  - [Running tests in CI](#running-tests-in-ci)
- [Writing new tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)
  - [Debugging CI](#debugging-ci)
  - [Authentication](#authentication)


> [!TIP]
> All shell commands shown assume you are cd'd into the `playwright/` directory

## Local setup

Setup playwright project dependencies:

```sh
npm install
# NOTE: do not overwrite existing files
npm init playwright@latest --yes -- . --quiet --browser=chromium
```

If you are using VS Code, it is also recommended that you [install the Playwright extension for VS Code](https://playwright.dev/docs/getting-started-vscode) and open the `playwright/` directory in its own editor session.

## Projects
We use Playwright projects for a separation of testing concerns.

### local
The "local" project performs test server setup, seeds the system, and runs tests against the local test server. All local end-to-end tests should be stored in the local folder. Any modifications that change either frontend or backend behavior should have an associated local end-to-end test for that specific change, as well as a new or updated user journey test that validates the change in the context of user flows throughout the app. Note: we will continue to add user journey tests and associated documentation as we flesh out our user stories.

The local project can be run by executing the command `make playwright-local` from within the root directory.

#### Local Test Data
When the local tests are spun up, a seedsystem.py script runs to randomly generate realistic test practitioners and organizations, as well as ones that satisfy certain test criteria. These records are used to test the system.

### uat
The "uat" project allows the dev to configure the base url, username, and password, allowing tests to be run against the deployed environments (please refer to the .env_template file for the environment variables that are expected). All uat tests should be stored in the uat folder. The UAT tests should verify that NPD meets the business requirements and user needs defined for each software stage. These are intended to support a test-driven development strategy, in which the business requirements are defined as code and the implementation is validated against those codified requirements. The automated UATs will not be required to be passing with each PR, but rather will give an indication of progress toward fulfilling feature, release, and/or product goals.

The uat project can be run with the command `npm run get-data-and-test` from within the playwright directory or `make playwright-uat` from within the root directory.

#### UAT Test Data
When the uat tests are spun up, test data are fetched from the NPI registry, according to the environment variables specified (see .env_template for examples).
* No environment variables: Dr. Oz's record is used as the default test practitioner record (stored in `/test-data/practitioner-sample.ts`) and New York Presbyterian Hospital is used as the default test organization record (stored in `/test-data/organization-sample.ts`)
* `NPI_LIST`: if the `NPI_LIST` environment variable is specified and contains a comma-separated list of NPIs, then the records associated with those NPIs will be fetched and used as test data.
* `RANDOM`: if the `RANDOM` environment variable is specified and set to `true`, then a random sampling of NPIs will be fetched and used as test data. `RANDOM_QUANTITY` specifies the number of random records that should be fetched (default 5).

## Running tests

### Locally

The test suite will start the test-server if it is not already running:

```sh
npx playwright test --project=local
```

If you want live rebuilds of frontend assets and to control the test-server separately, you can start those jobs in different shells.

```sh
# shell 1, project root
make watch-frontend-test-assets

# shell 2, project root
make test-server
```

### Running tests in CI

By default, Playwright assumes the test server is already running. You can disable this behavior and force Playwright to start its own test web server by setting `CI=True` in your shell:

```sh
cd playwright
CI=true npx get-data-and-test
```

This command will cause Playwright to launch the test-server (including rebuilding the database and compiling frontend assets) in docker and then shut it down at the end of the test suite.

## Writing new tests

The easiest way to write tests is with [codegen](https://playwright.dev/docs/codegen), a tool for writing test code by clicking in a browser. You can generate tests against the test-server by running:

```sh
npx playwright codegen localhost:8008
```

ALWAYS READ OVER THE TEST CODE BEFORE COMMITTING. It will not follow project conventions.

## Troubleshooting

### Debugging CI

Test failing in CI but not locally? Set `CI=true` before running tests locally and see what happens:

```sh
# from project root
docker compose down

cd playwright

CI=true npx playwright test
```

The GitHub Actions also uploads a full report whenever tests fail. Download and unzip the artifact .zip file and pass the resulting directory to `npx playwright show-report [DIRECTORY]` to see a full trace of the failed test.

```sh
# in Finder, unzip ~/Downloads/playwright-report.zip to ~/Downloads/playwright-report
npx playwright show-report ~/Downloads/playwright-report
```

Then find the failing test and click "View Trace".

### Authentication

If you sign-out inside a test which uses the default `auth.setup.ts` session, all subsequent tests which expect to be signed in will fail.

`auth.setup.ts` creates a single user session and if any test signs that session out, Django (correctly) will recognize that the cookie stored in `tests/.auth/user.json` is no longer valid. So even though the cookie is still present in every test, the session ID it names is signed out.