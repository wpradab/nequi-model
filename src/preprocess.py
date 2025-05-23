import boto3
import socket
import psycopg2
import pandas as pd
from utils import preprocess_tweet, safe_detect_language, get_secret

def load_secrets():
    """Carga los secretos de configuración desde la fuente segura."""
    return get_secret()

def create_s3_client():
    """Crea un cliente de AWS S3."""
    return boto3.client('s3')

def get_latest_file_from_s3(s3_client, bucket_name):
    """Obtiene el archivo más reciente del bucket S3."""
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    if 'Contents' not in response:
        raise ValueError("No hay archivos en el bucket.")
    latest_file = max(response['Contents'], key=lambda x: x['LastModified'])
    return latest_file['Key']

def load_data_from_s3(s3_client, bucket_name, file_key, nrows=5000):
    """Carga el archivo CSV directamente desde S3 usando pandas."""
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    df = pd.read_csv(obj['Body'], sep=',', nrows=nrows)
    print(df.head())
    return df

def preprocess_data(df):
    """Preprocesa los tweets, detecta idioma y filtra solo inglés."""
    df['clean_text'] = df['text'].apply(preprocess_tweet)
    df['language'] = df['clean_text'].apply(safe_detect_language)
    df_english = df[df['language'] == 'en'].copy()
    df_english['created_at'] = pd.to_datetime(df_english['created_at'], errors='coerce')
    return df_english

def check_redshift_connection(hostname, port, timeout=10):
    """Verifica la conexión TCP al cluster Redshift."""
    try:
        sock = socket.create_connection((hostname, port), timeout=timeout)
        print(f'Conexión exitosa a {hostname}:{port}')
        sock.close()
    except Exception as e:
        print(f'Error de conexión: {e}')

def connect_to_db(host, port, dbname, user, password):
    """Establece la conexión a la base de datos."""
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    return conn

def insert_tweets_into_db(conn, df):
    """Inserta los tweets procesados en la tabla."""
    cur = conn.cursor()
    insert_query = """
        INSERT INTO public.tweets_process (
            tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id, clean_text
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    for _, row in df.iterrows():
        cur.execute(insert_query, (
            row['tweet_id'], row['author_id'], row['inbound'], row['created_at'],
            row['text'], row['response_tweet_id'], row['in_response_to_tweet_id'], row['clean_text']
        ))
    conn.commit()
    cur.close()

def main():
    secrets = load_secrets()
    host = secrets["host"]
    port = secrets["port"]
    dbname = secrets["dbname"]
    user = secrets["username"]
    password = secrets["password"]

    bucket_name = 'tweets-test-123'
    s3_client = create_s3_client()

    latest_file_key = get_latest_file_from_s3(s3_client, bucket_name)
    df = load_data_from_s3(s3_client, bucket_name, latest_file_key)
    df_english = preprocess_data(df)

    check_redshift_connection(host, port)

    conn = connect_to_db(host, port, dbname, user, password)
    insert_tweets_into_db(conn, df_english)
    conn.close()

if __name__ == '__main__':
    main()
