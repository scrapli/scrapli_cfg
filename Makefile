lint:
	python -m isort .
	python -m black .
	python -m pylama .
	python -m pydocstyle .
	python -m mypy --strict scrapli_cfg/

darglint:
	find scrapli_cfg -type f \( -iname "*.py"\) | xargs darglint -x

cov:
	python -m pytest \
	--cov=scrapli_cfg \
	--cov-report html \
	--cov-report term \
	tests/

.PHONY: docs
docs:
	python docs/generate/generate_docs.py

deploy_docs:
	mkdocs gh-deploy
