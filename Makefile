.PHONY: check install uninstall

check:
	@echo -e "\nSjekker config"
	@echo "--------------"
	python validate_config.py
	@echo '\nKjør "sudo systemctl enable timeedit.timer" for å enable timeren'

install:
	@echo -e "\nInstallerer script og config"
	@echo "----------------------------"
	install -d /opt/timeedit/
	install -m 755 timeedit.py /opt/timeedit/
	install -m 644 config.py /opt/timeedit/
	@echo -e "\nInstallerer service og timer"
	@echo "----------------------------"
	install -m 644 timeedit.service /usr/lib/systemd/system/
	install -m 644 timeedit.timer /usr/lib/systemd/system/

uninstall:
	@echo -e "\nFjerner skript og config"
	@echo "------------------------"
	rm /opt/timeedit/timeedit.py
	rm /opt/timeedit/config.py
	rmdir /opt/timeedit
	@echo -e "\nDisabler service og timer"
	@echo "-------------------------"
	systemctl disable timeedit.service
	systemctl disable timeedit.timer
	@echo -e "\nFjerner service og timer units"
	@echo "------------------------------"
	rm /usr/lib/systemd/system/timeedit.service
	rm /usr/lib/systemd/system/timeedit.timer
