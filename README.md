# rpi-bitbang-spiflash
Bit bang an SPI interface to modify an SPI flash's register.

Currently tries to clear the QE (quad enable) bit in the sreg2 of a W25Q40BV or similar.
Useful for using an ESP8266 ESP-12F module as an SDIO wifi card (https://hackaday.io/project/8678-rpi-wifi).

Released into the public domain.
