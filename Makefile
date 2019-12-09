build:
	@docker build -t x0rzkov/laffka:alpine3.10-p3.7 .

run:
	@docker run -ti -p 5000:5000 -p 5678:5678 x0rzkov/laffka:alpine3.10-p3.7
