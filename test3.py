import dropbox


def upload_file_to_dropbox(file_url, dropbox_path):
    response = client.files_save_url(dropbox_path, file_url)
    return response

access_token = 'sl.Bg2pPDXgB-faWuiZVUxgDZpxBnwgZ3KL19UM1j3oSwja1ivxGur8SMjo_WHylWhGzdgMgUfowrcaozh3kS7lLACKbJqNL6i9JNp15a-920C4msmHuka-h8hulnBzU6S69sbJGTs'
client = dropbox.Dropbox(access_token)

file_url = 'https://spb.cian.ru/sale/flat/286944730/'
dropbox_path = '/page.html'
response = upload_file_to_dropbox(file_url, dropbox_path)
print(response)
