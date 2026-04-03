import json
import time
import logging
import pandas as pd
from kafka import KafkaConsumer
from sklearn.ensemble import RandomForestRegressor

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_consumer():
    while True:
        try:
            consumer = KafkaConsumer(
                'sensores',
                bootstrap_servers=['10.5.0.3:9092'],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='modelo-ia-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("✅ Modelo IA conectado ao Kafka (10.5.0.3)!")
            return consumer
        except Exception as e:
            logger.error(f"❌ Erro de conexão: {e}. Tentando em 5s...")
            time.sleep(5)

def main():
    consumer = conectar_consumer()
    dados_treino = []
    historico_grafico = [] # Lista para o gráfico do frontend
    regr = RandomForestRegressor(n_estimators=100, random_state=42)
    
    logger.info("📥 Aguardando dados para iniciar predições...")

    for message in consumer:
        try:
            ponto = message.value
            dados_treino.append(ponto)
            
            # Treina/Prediz quando tivermos dados suficientes
            if len(dados_treino) >= 5:
                df = pd.DataFrame(dados_treino)
                X = df[['temperatura', 'umidade']]
                y = df['pressao']
                
                regr.fit(X, y)
                
                # Predição para o ponto atual
                atual_X = pd.DataFrame([[ponto['temperatura'], ponto['umidade']]], columns=['temperatura', 'umidade'])
                previsao = regr.predict(atual_X)[0]
                
                # Adiciona ao histórico do gráfico
                ponto_grafico = {
                    'hora': time.strftime('%H:%M:%S'),
                    'real': round(ponto['pressao'], 2),
                    'previsao': round(float(previsao), 2)
                }
                historico_grafico.append(ponto_grafico)

                # Limita o histórico a 20 pontos para o gráfico não poluir
                if len(historico_grafico) > 20:
                    historico_grafico.pop(0)

                # Monta o objeto final para o JSON
                resultado = {
                    'ultima_leitura': ponto,
                    'previsao_pressao': round(float(previsao), 2),
                    'data_processamento': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'historico': historico_grafico
                }

                with open('previsao.json', 'w') as f:
                    json.dump(resultado, f)
                
                logger.info(f"🔮 Real: {ponto_grafico['real']} | Previsto: {ponto_grafico['previsao']}")

                # Mantém o dataframe de treino leve
                if len(dados_treino) > 100:
                    dados_treino.pop(0)

        except Exception as e:
            logger.error(f"⚠️ Erro: {e}")

if __name__ == "__main__":
    main()
