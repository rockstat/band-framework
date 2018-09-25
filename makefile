bump-patch:
	bumpversion patch

bump-minor:
	bumpversion minor

build_image:
	docker build -t rockstat/band-base-py .

to_master:
	sh -c 'git checkout master && git merge dev && git push origin master && git checkout dev'
