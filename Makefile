IMG=cuts:devel
STACK=cuts
FLNAME=cuts_cuts_1

.PHONY: help clean docker down exec run stop up watch

help:
	@echo "Make what? Try: clean, docker, down, exec, run, stop, up, watch"
	@echo '    where: help    - show this help message'
	@echo '           clean   - remove all cache files'
	@echo '           docker  - build a Flask/Gunicorn server container image'
	@echo '           down    - stop a Cuts server stack'
	@echo '           exec    - exec into the running Flask server container'
	@echo '           run     - start a standalone Flask server container, for testing'
	@echo '           stop    - stop a running standalone Flask server container'
	@echo '           up      - start a Cuts server stack'
	@echo '           watch   - show logfile for a running Flask server container'

clean:
	rm -rf config/__pycache__
	rm -rf cuts/__pycache__
	rm -rf cuts/blueprints/__pycache__
	rm -rf cuts/blueprints/img/__pycache__
	rm -rf cuts/blueprints/pages/__pycache__
	rm -rf cuts/static/__pycache__

docker:
	docker build -t ${IMG} .

down:
	docker stack rm ${STACK}

up:
	docker stack deploy -c docker-compose.yml ${STACK}


exec:
	docker cp .bash_env ${FLNAME}:/etc/bash_env.trh
	docker exec -it ${FLNAME} bash

run:
	docker run -d --rm --name ${FLNAME} -p 8000:8000 -v ${PWD}/images:/vos/images:ro ${IMG}

stop:
	docker stop ${FLNAME}

watch:
	docker logs -f ${FLNAME}

%:
	@:
