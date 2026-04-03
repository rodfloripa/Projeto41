import time
import json
import random
import logging
from kafka import KafkaProducer

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_producer():
    """Tenta conectar ao Kafka usando o IP fixo definido no docker-compose"""
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['10.5.0.3:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all' # Garante que a mensagem foi recebida
            )
            logger.info("✅ Sensor conectado ao Kafka no IP 172.20.0.3!")
            return producer
        except Exception as e:
            logger.error(f"⏳ Aguardando Kafka (Sensor)... Erro: {e}")
            time.sleep(5)

def gerar_dados():
    return {
        'temperatura': round(random.uniform(20.0, 32.0), 2),
        'umidade': round(random.uniform(40.0, 70.0), 2),
        'pressao': round(random.uniform(1000.0, 1015.0), 2),
        'timestamp': time.time()
    }

def main():
    producer = conectar_producer()
    topic = 'sensores'

    logger.info(f"🚀 Iniciando envio de dados para o tópico: {topic}")
    
    try:
        while True:
            dados = gerar_dados()
            producer.send(topic, dados)
            logger.info(f"📡 Dados enviados: {dados}")
            time.sleep(2) # Envia a cada 2 segundos
    except KeyboardInterrupt:
        logger.info("Fechando sensor...")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
