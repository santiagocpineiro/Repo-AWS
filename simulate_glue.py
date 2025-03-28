import boto3
import pandas as pd
from io import BytesIO
from collections import defaultdict

# Configuración de boto3 para LocalStack
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',  # Credenciales dummy para LocalStack
    aws_secret_access_key='test',
    region_name='us-east-1'
)

# Paso 1: Listar todos los archivos JSON en el bucket S3
bucket_name = 'logs-bucket'
prefix = 'logs/'  # Prefijo del directorio donde están los archivos


def list_s3_files(bucket, prefix):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    return files


files = list_s3_files(bucket_name, prefix)
print(f"Archivos encontrados en el bucket: {files}")

# Paso 2: Agrupar archivos por día
files_by_date = defaultdict(list)

for file_key in files:
    # Extraer la fecha del nombre del archivo
    try:
        date_part = file_key.split('/')[-1].split('T')[0]  # Ejemplo: "2025-03-28"
    except IndexError:
        print(f"Archivo con nombre inválido: {file_key}")
        continue

    files_by_date[date_part].append(file_key)

print("Archivos agrupados por día:")
for date, file_list in files_by_date.items():
    print(f"{date}: {file_list}")

# Paso 3: Procesar archivos por día
for date, file_list in files_by_date.items():
    print(f"Procesando archivos para la fecha: {date}")

    dfs = []
    for file_key in file_list:
        print(f"Leyendo archivo: {file_key}")

        # Obtener el contenido del archivo JSON
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        print(f"Contenido del archivo: {file_content}")  # Depuración

        try:
            # Crear un DataFrame con el contenido del archivo JSON
            data = pd.DataFrame({
                'filename': [file_key.split('/')[-1]],  # Nombre del archivo
                'detail': [file_content]  # Contenido completo del archivo JSON
            })
        except Exception as e:
            print(f"Error al procesar el archivo {file_key}: {e}")
            continue

        dfs.append(data)

    # Combinar todos los DataFrames en uno solo para el día
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"Datos combinados para la fecha {date}:")
        print(combined_df)
    else:
        print(f"No se encontraron datos válidos para la fecha {date}.")
        continue

    # Paso 4: Guardar el DataFrame combinado en S3 como un archivo CSV
    output_key = f'processed_data/{date}_data.csv'
    csv_buffer = BytesIO()
    combined_df.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=bucket_name, Key=output_key, Body=csv_buffer.getvalue())

    print(f"Datos combinados guardados en S3: s3://{bucket_name}/{output_key}")

    # Paso 5: Simular la creación de la tabla única para el día
    database_name = 'mi_database'
    table_name = f'mi_tabla_{date}'  # Nombre de la tabla basado en la fecha

    print(f"Base de datos simulada '{database_name}' creada.")
    print(f"Tabla simulada '{table_name}' creada con los siguientes campos:")
    print(", ".join(combined_df.columns))

# Fin del script