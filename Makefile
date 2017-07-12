unzip:
	cd ./data/Boundary_datasets && unzip "*.zip"

.PHONY: all clean unzip
all: unzip
	# all: make complete

clean:
	rm figures/*
	# clean: make complete
