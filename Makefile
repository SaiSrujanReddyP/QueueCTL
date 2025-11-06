.PHONY: help install test demo clean run-workers stop-workers status

help:
	@echo "QueueCTL - CLI Job Queue System"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install dependencies and setup"
	@echo "  test        - Run comprehensive test suite"
	@echo "  demo        - Run interactive demo"
	@echo "  clean       - Clean up generated files"
	@echo "  run-workers - Start 3 workers"
	@echo "  stop-workers- Stop all workers"
	@echo "  status      - Show system status"
	@echo ""
	@echo "Example usage:"
	@echo "  make install"
	@echo "  make demo"
	@echo "  python queuectl.py enqueue '{\"id\":\"test\",\"command\":\"echo hello\"}'"
	@echo "  make run-workers"

install:
	@echo "Setting up QueueCTL..."
	python setup.py

test:
	@echo "Running test suite..."
	python test_simple.py

demo:
	@echo "Running demo..."
	python demo_simple.py

test-full:
	@echo "Running full test suite..."
	python test_queuectl.py

demo-full:
	@echo "Running full demo..."
	python demo.py

clean:
	@echo "Cleaning up..."
	rm -f jobs.db
	rm -rf locks/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	find . -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

run-workers:
	@echo "Starting 3 workers..."
	python queuectl.py worker start --count 3

stop-workers:
	@echo "Stopping workers..."
	python queuectl.py worker stop

status:
	@echo "System status:"
	python queuectl.py status