PERCENT := %
DEL := /

DOCK_APP := band-base-py
DOCK_REPO := rockstat/
TAG_DEV := 3.7-dev
TAG := 3.7

bump-patch:
	bumpversion patch

bump-minor:
	bumpversion minor

build_image:
	docker build -t $(DOCK_APP) .
	docker tag band-base-py $(DOCK_REPO)$(DOCK_APP):$(TAG_DEV)
	docker tag band-base-py $(DOCK_REPO)$(DOCK_APP):$(TAG)

push_image_dev:
	docker push $(DOCK_REPO)$(DOCK_APP):$(TAG_DEV)

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
