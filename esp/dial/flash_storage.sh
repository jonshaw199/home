idf.py build
esptool.py --chip esp32s3 write_flash -z 0x110000 build/storage.bin