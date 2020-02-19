ENVLOC=/etc/trhenv
IMG=cuts:devel
IMGS=${PWD}/images
NAME=dev_cuts
PROG=Cuts
STACK=vos
TSTIMG=cuts:test

.PHONY: help clean down exec run runt stop up watch

help:
	@echo "Make what? Try: clean, docker, dockert, down, exec, run, runt, stop, up, watch"
	@echo '  where:'
	@echo '     help    - show this help message'
	@echo '     clean   - remove all cache files'
	@echo '     docker  - build a production ${PROG} server container image'
	@echo '     dockert - build a server container image with tests (for testing)'
	@echo '     down    - stop a running ${PROG} server stack (for development)'
	@echo '     exec    - exec into running ${PROG} server (CLI arg: NAME=containerID)'
	@echo '     run     - start a standalone ${PROG} server container (for development)'
	@echo '     runt    - run tests and code coverage in a standalone container'
	@echo '     stop    - stop a running standalone ${PROG} server container'
	@echo '     up      - start a ${PROG} server stack (for development)'
	@echo '     watch   - show logfile for a running ${PROG} server container'

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

exec:
	docker cp .bash_env ${NAME}:${ENVLOC}
	docker exec -it ${NAME} bash

run:
	docker run -d --rm --name ${NAME} -p 8000:8000 -v ${IMGS}:/vos/images:ro ${IMG}

runt:
	docker run -d --rm --name ${NAME} -p 8000:8000 -v ${IMGS}:/vos/images:ro ${TSTIMG}
	docker exec -it ${NAME} py.test -vv --cov-report term-missing --cov /cuts
	docker stop ${NAME}

stop:
	docker stop ${NAME}

up:
	docker stack deploy -c docker-compose.yml ${STACK}

watch:
	docker logs -f ${NAME}
