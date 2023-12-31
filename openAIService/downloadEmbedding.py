from google.cloud import storage
import os

def download_embedding(bucket_name, credentials_path, destination_folder):
    # Configura las credenciales del cliente usando la ruta del archivo json
    store_client = storage.Client.from_service_account_json(credentials_path)
    
    # Crea un objeto de bucket
    bucket = store_client.bucket(bucket_name)
    
    # Nombres de los archivos a descargar
    files_to_download = ["PdfVectorStore/faiss_index/index.faiss", "PdfVectorStore/faiss_index/index.pkl"]

    # Descargar cada archivo
    for file_name in files_to_download:
        blob = bucket.blob(file_name)
        destination_file_name = os.path.join(destination_folder, file_name.split('/')[-1])
        try:
            blob.download_to_filename(destination_file_name)
            print(f"Descargado {file_name} a {destination_file_name}")
        except Exception as e:
            print(f"No se pudo descargar el archivo {file_name}: {e}")

# Ejemplo de cómo llamar a la función:
# Asegúrate de proporcionar la ruta al archivo json de credenciales y el nombre del bucket adecuadamente.
# El parámetro destination_folder es la carpeta local donde quieres guardar los archivos descargados.
# download_embedding("vectorstore-chatbot", "path/to/your/credentials.json", "local/folder/destination")
