
# copy all services into systemd folder
sudo cp services/usb-mount.service /etc/systemd/system
sudo cp services/usb-unmount.service /etc/systemd/system
sudo cp services/sh_ABV.service /etc/systemd/system

# reload daemon
sudo systemctl daemon-reload

# enable all of the services 
sudo systemctl enable usb-mount.service
sudo systemctl enable usb-unmount.service
sudo systemctl enable sh_ABV.service

