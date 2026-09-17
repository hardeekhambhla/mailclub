SHELL := /bin/bash
DIR := $(shell pwd)
USER_NAME := $(shell whoami)
VENV := .venv/bin
SERVICE := mailclub.service
UNIT_PATH := /etc/systemd/system/$(SERVICE)

.PHONY: install run status logs uninstall start stop restart

.venv/.installed: requirements.txt
	python3 -m venv .venv
	$(VENV)/pip install -q --upgrade pip
	$(VENV)/pip install -q -r requirements.txt
	touch .venv/.installed

install: .venv/.installed
	sed -e "s|__USER__|$(USER_NAME)|g" -e "s|__DIR__|$(DIR)|g" mailclub.service.template > /tmp/$(SERVICE)
	sudo mv /tmp/$(SERVICE) $(UNIT_PATH)
	sudo systemctl daemon-reload
	sudo systemctl enable --now $(SERVICE)
	@echo "Installed and started. Check: make status"

uninstall:
	sudo systemctl disable --now $(SERVICE) || true
	sudo rm -f $(UNIT_PATH)
	sudo systemctl daemon-reload

run: .venv/.installed
	$(VENV)/python app.py

start:
	sudo systemctl start $(SERVICE)

stop:
	sudo systemctl stop $(SERVICE)

restart:
	sudo systemctl restart $(SERVICE)

status:
	systemctl status $(SERVICE)

logs:
	journalctl -u $(SERVICE) -f
