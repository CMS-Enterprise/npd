# npdfhir

Django backend that provides a FHIR API for accessing data from the npd database and supporting code for the National Provider Directory search web application.

## Project structure

* `backend/` contains code for deploying the application within a docker container
* `backend/app/` directory contains code that controls the overall application
* `backend/npdfhir/` contains code that drives the FHIR API
* `backend/provider_directory/` contains code that drives the landing page and search application

## Contributing to the API

### Prerequesites

- [docker](https://www.docker.com/)
- [colima](https://github.com/abiosoft/colima) (if using macOS)
- a postgres database with the npd schema

### Local dev

1. Ensure that either colima (if using macOS) or the docker service is running
2. Create a `.env` file in this directory, following the template of the `.env_template` file
    * n.b. ensure that NPD_DB_HOST is set to `db` if using a local postgres instance.
3. Run `docker-compose up --build` from the project root and following any changes
4. Happy coding!

### Running Tests

Without docker:

1. Ensure that you have a running local postgres instance
2. Make sure that you have a working `.env` file as described above
3. Make sure all python dependencies are installed in a venv or otherwise
4. Navigate to the `backend/` directory and run `python manage.py test`

All commands below

With docker, full setup every time:

1. Run `make test` from project root

With docker, setup once:

1. (one-time) Run `make test-setup`
2. Run `make test-backend`

### Automated Testing

Automated tests run in a GitHub workflow whenever a PR is created or a push is made to the main branch. All tests must pass for PRs to be accepted.

### Code quality

We use [ruff](https://docs.astral.sh/ruff) to lint and format all Python in this project. All PRs must pass the linter to be accepted.

You can install ruff with `pip install ruff`, `brew install ruff`, or `make install-tools` and run it natively or with the `make lint` command.

```sh
make lint
# runs `ruff check .`
```

You can format all code in the project with `make format`, or rely on the pre-commit hooks installed by `make install-tools` to format just the files you are making changes to.

## Documentation


API documentation can be viewed at `/fhir/docs`. If you make any changes to the Views, please update the swagger schema accordingly!

## Understanding the Flow of Data through the FHIR API

![Flowchart](practitioner_data_flow.png)