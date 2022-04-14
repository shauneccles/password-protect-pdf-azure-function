# Password Protect PDF Azure Function

Password Protect PDF Azure Function does what it says on the label - takes a PDF file and uses the Py2PDF Python library to password protect it and return the file.

## Installation

You can use the Deployment Zip Push method if you wish - download this repository as a Zip and then upload using Azure CLI.

```bash
az functionapp deployment source config-zip -g <resource_group> -n \
<your-function-name> --src password-protect-pdf-azure-function-main.zip
```

## Usage

Submit a file via form upload with a PDF file to the Function URL with the password appended - an encrypted PDF will be returned.

```
curl -X GET \
  'http://<your-azure-function-location>/api/<your-function-name>?password=your_password' \
  --form 'file=@C:\your_test_file.pdf'
```


## Contributing
Pull requests are welcome - this does what I need and should hopefully be clear enough to help you tailor it as required.

## License
[MIT](https://choosealicense.com/licenses/mit/)
