.PHONY: backend-test frontend-build audit eval smoke verify

backend-test:
	cd backend && pytest -q

frontend-build:
	cd frontend && npm run build

audit:
	cd frontend && npm audit --audit-level=moderate

eval:
	python scripts/run_evaluation.py

smoke:
	python scripts/smoke_test.py

verify: backend-test frontend-build audit eval smoke

