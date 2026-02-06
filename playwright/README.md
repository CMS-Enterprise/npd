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

## Running tests

### Locally

The test suite will start the test-server if it is not already running:

```sh
npx playwright test
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
CI=true npx playwright test
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