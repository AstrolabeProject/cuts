IMG=cuts
STACK=cuts
FLNAME=cuts_web_1

.PHONY: help build clean docker exec run stop watch

help:
	@echo "Make what? Try: clean, devdown, devup, prodown, proup, docker, exec, run, stop, watch"
	@echo '    where: help    - show this help message'
	@echo '           clean   - remove all cache files'
	@echo '           devdown - stop a reloading Flask stack in development mode'
	@echo '           devup   - start a reloading Flask stack in development mode'
	@echo '           prodown - stop a Cuts server production stack'
	@echo '           proup   - start a Cuts server stack in production mode'
	@echo '           docker  - build a Flask server container image'
	@echo '           exec    - exec into the running Flask server container'
	@echo '           run     - start a standalone Flask server container, for testing'
	@echo '           stop    - stop a running standalone Flask server container'
	@echo '           watch   - show logfile for a running Flask server container'

clean:
	rm -rf config/__pycache__
	rm -rf cuts/__pycache__
	rm -rf cuts/static/__pycache__

devdown:
	docker-compose down

devup:
	docker-compose up

docker:
	docker build -t ${IMG} .

prodown:
	docker stack rm ${STACK}

proup:
	docker stack deploy -c docker-compose-prod.yml ${STACK}


exec:
	docker exec -it ${FLNAME} bash

run:
	docker run -d --rm --name ${FLNAME} -p 8000:8000 -v ${PWD}/images:/vos/images:ro ${IMG}

stop:
	docker stop ${FLNAME}

watch:
	docker logs -f ${FLNAME}

%:
	@:
