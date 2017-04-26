.PHONY: all \
        clean \
        dist \
        help \
        install \
        release \
        sdist \
        wheel

all: clean dist

define USAGE
Targets:

  clean    remove build artifacts
  dist     build source distribution and wheel
  install  install package to active Python site packages
  release  build and upload package to PyPI
  sdist    build source distribution
  wheel    build wheel

endef

help:
	$(info $(USAGE))

clean:
	$(RM) -r build dist
	find . -name '*.pyc' -delete
	find . -name '*.egg-info' -exec $(RM) -r {} +
	find . -name '*.egg' -delete
	find . -name '__pycache__' -exec $(RM) -r {} +

dist: sdist wheel

install:
	python setup.py install

release: dist
	twine upload dist/*.whl dist/*.tar.gz

sdist: clean
	python setup.py sdist

wheel: clean
	python setup.py bdist_wheel
