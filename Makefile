PYTHON_VERSIONS:=3.6,3.7,3.7-dev,3.9

export PYTHON_VERSIONS

.PHONY: test

test_setup:
	./scripts/test-setup.sh

test: clean test_setup
	./scripts/run-tests.sh

coverage_report: test
	@coverage html && echo 'Please open "htmlcov/index.html" in a browser.'

pip_compile:
	./scripts/pip-compile.sh

clean:
	rm -rf usr/ etc/ *.deb build dist
	find . -name "*.pyc" -delete

release_setup: clean
	git clean -ffdx -e .idea

release: release_setup
	./scripts/release.sh
