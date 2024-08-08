Running Tests
=============

- All tests are in the ``test`` directory.
- Some tests require docker images. In particular, the ``test_pacs`` module, requires a PACS. There is a ``docker-compose.yml`` file in ``test/`` that should have everything you need to run all tests.
- There is a target in ``Makefile`` called ``tests``: ``make tests`` will launch the ``docker-compose.yml`` and run tests.

