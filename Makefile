
zip: clean
	zip upload_to_lambda.zip *.py

clean:
	rm -f upload_to_lambda.zip
