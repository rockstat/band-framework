PERCENT := %
DEL := /

bump-patch:
	bumpversion patch

bump-minor:
	bumpversion minor

build_image:
	docker build -t band-base-py .
	docker tag band-base-py rockstat/band-base-py:dev

push_image_dev:
	docker push rockstat/band-base-py:dev

to_master:
	sh -c 'git checkout master && git merge dev && git push origin master && git checkout dev'

travis-trigger:
	curl -vv -s -X POST \
		-H "Content-Type: application/json" \
		-H "Accept: application/json" \
		-H "Travis-API-Version: 3" \
		-H "Authorization: token $$TRAVIS_TOKEN" \
		-d '{ "request": { "branch":"$(br)" }}' \
		https://api.travis-ci.com/repo/$(subst $(DEL),$(PERCENT)2F,$(repo))/requests
