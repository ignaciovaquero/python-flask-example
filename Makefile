.PHONY: test

test:
	pytest --cov=. tests/

type:
	pytype guest.py app.py controller.py
