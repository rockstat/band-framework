
patch:
	bumpversion patch

minor:
	bumpversion minor

build_image:
	docker build -t rockstat/band-base-py .
