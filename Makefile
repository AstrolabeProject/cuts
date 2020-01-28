ENVLOC=/etc/trhenv
IMG=cuts:devel
IMGS=${PWD}/images
STACK=vos
TSTIMG=cuts:test
NAME=dev_cuts

.PHONY: help clean docker down exec run stop up watch

help:
	@echo "Make what? Try: clean, docker, down, exec, run, stop, up, watch"
	@echo '    where: help     - show this help message'
	@echo '           clean    - remove all cache files'
	@echo '           docker   - build a production server container image'
	@echo '           dockert  - build a server container image with tests (for testing)'
	@echo '           down     - stop a Cuts server stack'
	@echo '           exec     - exec into running Flask server (CLI arg: NAME=containerID)'
	@echo '           run      - start a standalone Flask server container'
	@echo '           runt     - start a standalone Flask server container (for testing)'
	@echo '           stop     - stop a running standalone Flask server container'
	@echo '           test     - execute all tests in the running standalone Flask server container'
	@echo '           up       - start a Cuts server stack (for development)'
	@echo '           watch    - show logfile for a running Flask server container'

clean:
	rm -rf config/__pycache__
	rm -rf cuts/__pycache__
	rm -rf cuts/blueprints/__pycache__
	rm -rf cuts/blueprints/img/__pycache__
	rm -rf cuts/blueprints/pages/__pycache__
	rm -rf cuts/static/__pycache__

docker: clean
	docker build -t ${IMG} .

dockert: clean
	docker build --build-arg TESTS=tests -t ${TSTIMG} .

down:
	docker stack rm ${STACK}

up:
	docker stack deploy -c docker-compose.yml ${STACK}

exec:
	docker cp .bash_env ${NAME}:${ENVLOC}
	docker exec -it ${NAME} bash

run:
	docker run -d --rm --name ${NAME} -p 8000:8000 -v ${IMGS}:/vos/images:ro ${IMG}

runt:
	docker run -d --rm --name ${NAME} -p 8000:8000 -v ${IMGS}:/vos/images:ro ${TSTIMG}

test:
	docker exec -it ${NAME} py.test --cov-report term-missing --cov /cuts

stop:
	docker stop ${NAME}

watch:
	docker logs -f ${NAME}
