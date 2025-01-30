import json
from azure.storage.blob import BlobServiceClient

def load_connection_string(config_path="S:/Snowball/config/account_integrations.json"):
    """
    Load the Azure connection string from the account_integrations.json file.
    """
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        return config["api_keys"]["azure_connection_string"]
    except KeyError as e:
        raise KeyError(f"Missing key in configuration: {e}")
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file not found.")

def test_azure_upload():
    connection_string = load_connection_string()
    container_name = "system-health-logs"
    blob_name = "test_blob.txt"
    test_file_path = "test_file.txt"

    # Create a test file
    with open(test_file_path, "w") as f:
        f.write("This is a test file for Azure Blob Storage upload.")

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        if not container_client.exists():
            raise Exception(f"Container '{container_name}' does not exist.")

        with open(test_file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True)

        print(f"Successfully uploaded {test_file_path} to Azure Blob Storage as {blob_name}.")
    except Exception as e:
        print(f"Azure upload failed: {e}")

if __name__ == "__main__":
    test_azure_upload()
