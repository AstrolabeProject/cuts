APP_ROOT=/cuts
CONIMGS=/vos/images
CONSCRIPTS=${APP_ROOT}/scripts
ENVLOC=/etc/trhenv
EP=/bin/bash
IMG=cuts:devel
IMGS=${PWD}/images
NET=vos_net
NAME=cuts
PORT=8000
PROG=Cuts
SCRIPTS=${PWD}/scripts
SHELL=/bin/bash
STACK=vos
TARG=${APP_ROOT}
TSTIMG=cuts:test

.PHONY: help docker dockert down exec run runt stop up watch

help:
	@echo "Make what? Try: docker, dockert, down, exec, run, runtc, runtep, stop, up, watch"
	@echo '  where:'
	@echo '    help    - show this help message'
	@echo '    bash    - run Bash in a ${PROG} container (for development)'
	@echo '    docker  - build a production ${PROG} server container image'
	@echo '    dockert - build a server container image with tests (for testing)'
	@echo '    down    - stop a running ${PROG} server stack (for development)'
	@echo '    exec    - exec into running ${PROG} server (CLI arg: NAME=containerID)'
	@echo '    run     - start a standalone ${PROG} server container (for development)'
	@echo '    runit   - run the runit program in a test container'
	@echo '    runt1   - run single test (TARG=testpath) w/ code coverage in test container'
	@echo '    runtc   - run all tests w/ code coverage in a test container'
	@echo '    stop    - stop a running standalone ${PROG} server container'
	@echo '    up      - start a ${PROG} server stack (for development)'
	@echo '    watch   - show logfile for a running ${PROG} server container'

bash:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:${CONIMGS}:ro --entrypoint ${SHELL} ${TSTIMG} ${ARGS}

docker:
	docker build -t ${IMG} .

dockert:
	docker build --build-arg TESTS=tests -t ${TSTIMG} .

down:
	docker stack rm ${STACK}

exec:
	docker cp .bash_env ${NAME}:${ENVLOC}
	docker exec -it ${NAME} bash

run:
	docker run -d --rm --name ${NAME} -p ${PORT}:${PORT} -v ${IMGS}:${CONIMGS}:ro ${IMG}

runit:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:${CONIMGS}:ro -v ${SCRIPTS}:${CONSCRIPTS} --entrypoint ./scripts/runit ${TSTIMG} ${ARGS}

runt1:
	docker run -it --rm --network ${NET} --name ${NAME} -p ${PORT}:${PORT} -v ${IMGS}:${CONIMGS}:ro --entrypoint pytest ${TSTIMG} -vv ${TARG}

runtc:
	docker run -it --rm --network ${NET} --name ${NAME} -p ${PORT}:${PORT} -v ${IMGS}:${CONIMGS}:ro --entrypoint pytest ${TSTIMG} -vv --cov-report term-missing --cov ${TARG}

stop:
	docker stop ${NAME}

up:
	docker stack deploy -c docker-compose.yml ${STACK}

watch:
	docker logs -f $$(docker ps -f name=vos_cuts -q)
