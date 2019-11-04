# -*- coding: utf-8 -*-

bind = '0.0.0.0:8000'
accesslog = '-'
access_log_format = '%(h)s %(u)s %(t)s "%(r)s" %(s)s %(b)s in %(D)sµs (%(L)ss)'
errorlog = '-'
reload = True

# workers configuration
workers = 2
worker_class = 'gevent'
worker_connections = 100
threads = 8
timeout = 120
