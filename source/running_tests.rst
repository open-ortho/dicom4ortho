Running Tests
=============

- All tests are in the ``test`` directory and use ``unittest``.
- Run unit tests with ``python -m unittest discover -s test -p "test_*.py"``.
- Some end-to-end tests require the Orthanc services defined in
  ``test/docker-compose.yml``.
- ``make test`` starts the Docker services, runs the full suite, and stops the
  services.
