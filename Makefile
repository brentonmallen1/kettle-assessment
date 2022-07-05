.PHONY: database teardown
database:
	docker compose up -d
teardown:
	docker compose down