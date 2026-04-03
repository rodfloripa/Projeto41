### Previsão em tempo real com Kafka

<p align="justify">Este projeto consiste em uma infraestrutura completa de <b>Monitoramento e Predição para Estufas Inteligentes</b>, integrando conceitos avançados de Engenharia de Dados (Big Data) e Ciência de Dados. O sistema simula a coleta de telemetria ambiental, transporta esses dados de forma resiliente, processa-os através de um modelo de Machine Learning e os exibe em um gráfico interativo em tempo real.</p>

Para rodar digite docker-compose up

Acesse http://localhost:8081/

<p align="justify"><h3>🛠 Tecnologias Utilizadas</h3></p>

<p align="justify"><ul>
<li><b>Docker & Docker Compose:</b> Para a orquestração de containers e isolamento de serviços.</li>
<li><b>Apache Kafka:</b> Como broker de mensagens de alta performance para o streaming de dados.</li>
<li><b>Apache NiFi:</b> Ferramenta de ingestão e orquestração de fluxos de dados (Dataflow).</li>
<li><b>Python:</b> Linguagem base para o sensor (produtor) e o modelo de ML(consumidor).</li>
<li><b>Scikit-Learn (Random Forest):</b> Algoritmo de ML para regressão e predição.</li>
<li><b>Pandas:</b> Para manipulação e estruturação dos dados em tempo real.</li>
<li><b>Nginx:</b> Servidor web de alto desempenho para hospedar a interface.</li>
<li><b>Chart.js:</b> Biblioteca JavaScript para a renderização de gráficos dinâmicos.</li>
</ul></p>

<p align="justify"><h3>📋 Relatório Técnico da Arquitetura</h3></p>

<p align="justify"><h4>1. O Orquestrador: docker-compose.yml</h4></p>

<p align="justify">Este arquivo é o coração da infraestrutura. Ele utiliza o conceito de Containers para garantir que cada serviço rode em um ambiente isolado, mas conectado.</p>

<p align="justify"><ul>
<li><b>Zookeeper & Kafka:</b> Formam a camada de mensageria. O Kafka atua como um "buffer" de alta performance que recebe os dados do sensor e os disponibiliza para o modelo de ML.</li>
<li><b>Rede Estática (10.5.0.x):</b> Configurada para evitar conflitos de IP e garantir que o Sensor e o Model sempre encontrem o Broker do Kafka.</li>
<li><b>Volumes:</b> Permitem que o arquivo <b>previsao.json</b> seja compartilhado entre o container de ML (que escreve) e o container Web (que lê).</li>
</ul></p>

<p align="justify"><b>Bloco em Destaque:</b></p>

``` 
YAML

networks:
  greenhouse_net:
    driver: bridge
    ipam:
      config:
        - subnet: 10.5.0.0/16 # Define a sub-rede fixa para evitar conflitos
``` 
<p align="justify"><h4>2. Ingestão e Fluxo: Apache NiFi</h4></p>

<p align="justify">O Apache NiFi atua como o orquestrador do fluxo de dados (Dataflow). Ele é responsável por coletar, filtrar e rotear as informações de telemetria entre os produtores e o barramento do Kafka.</p>

<p align="justify"><ul>
<li><b>Gerenciamento Visual:</b> Permite criar pipelines de dados complexos através de uma interface baseada em blocos (Processadores).</li>
<li><b>Roteamento Inteligente:</b> Pode direcionar dados para diferentes tópicos ou destinos dependendo do conteúdo da mensagem.</li>
<li><b>Controle de Contrapressão (Backpressure):</b> Garante que o sistema não seja sobrecarregado caso a produção de dados seja maior que a capacidade de consumo.</li>
</ul></p>

<p align="justify"><b>Bloco em Destaque:</b></p>

```
YAML

  nifi:
    image: apache/nifi:latest
    ports:
      - "8443:8443" # Interface para desenho do fluxo de dados
    networks:
      - greenhouse_net
```

<p align="justify"><h4>3. Barramento de Mensageria: Apache Kafka</h4></p>

<p align="justify">O Apache Kafka é a espinha dorsal do projeto, funcionando como um sistema de mensageria distribuída de altíssima performance. Ele garante que os dados enviados pelo NiFi ou pelos sensores fiquem disponíveis de forma persistente e ordenada para o modelo de Inteligência Artificial.</p>

<p align="justify"><ul>
<li><b>Desacoplamento:</b> Permite que o produtor (sensor) e o consumidor (IA) funcionem em velocidades diferentes sem perda de informação.</li>
<li><b>Tópicos Particionados:</b> Organiza os fluxos de dados (como o tópico <code>sensores</code>) para permitir escalabilidade futura.</li>
<li><b>Modo Zookeeper:</b> Utiliza o Zookeeper para gerenciar o estado do cluster e a eleição de líderes, garantindo que o broker esteja sempre disponível.</li>
</ul></p>

<p align="justify"><b>Bloco em Destaque no Docker:</b></p>

```
YAML

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 10.5.0.2:2181
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://10.5.0.3:9092,EXTERNAL://localhost:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_ENABLE_KRAFT: "false" # Força o uso do Zookeeper para estabilidade
    networks:
      greenhouse_net:
        ipv4_address: 10.5.0.3
```

<p align="justify"><h4>4. O Produtor de Dados: sensor.py</h4></p>

<p align="justify">Este bloco simula o hardware (sensores físicos) da estufa, gerando o fluxo contínuo de dados (Streaming).</p>

<p align="justify"><ul>
<li><b>Gerador de Telemetria:</b> Utiliza a biblioteca <b>random</b> para criar variações de temperatura, umidade e pressão.</li>
<li><b>KafkaProducer:</b> Conecta-se ao Broker no IP <b>10.5.0.3</b>. Ele serializa os dados em JSON e os envia para o tópico sensores.</li>
<li><b>Resiliência:</b> Possui lógica de retry automática para aguardar a inicialização do Kafka.</li>
</ul></p>

<p align="justify"><b>Bloco em Destaque:</b></p>

``` 
Python

def gerar_dados():
    return {
        'temperatura': round(random.uniform(20.0, 32.0), 2),
        'umidade': round(random.uniform(40.0, 70.0), 2),
        'pressao': round(random.uniform(1000.0, 1015.0), 2),
        'timestamp': time.time()
    }
```

<p align="justify"><h4>5. O Cérebro: model.py</h4></p>

<p align="justify">Este é o bloco de Machine Learning e processamento analítico.</p>

<p align="justify"><ul>
<li><b>Treinamento Online (RandomForestRegressor):</b> O script acumula os dados recebidos e re-treina a floresta aleatória dinamicamente.</li>
<li><b>Lógica de Predição:</b> O modelo utiliza a Temperatura e a Umidade para prever a Pressão Atmosférica.</li>
<li><b>Gerenciador de Histórico:</b> Mantém uma lista circular dos últimos 20 registros para alimentar o gráfico.</li>
</ul></p>

<p align="justify"><b>Bloco em Destaque:</b></p>

```  
Python

# Treinamento e predição com Scikit-Learn
regr.fit(df[['temperatura', 'umidade']], df['pressao'])
previsao = regr.predict(atual_X)[0]
``` 
<p align="justify"><h4>6. O Visualizador: index.html</h4></p>

<p align="justify">A interface do usuário que transforma dados brutos em decisões visuais.</p>

<p align="justify"><ul>
<li><b>Chart.js:</b> Renderiza um gráfico de linhas dinâmico comparando a linha do "Real" (sensor) com a "Predição" (IA).</li>
<li><b>Tratamento de Cache:</b> Utiliza um parâmetro dinâmico na URL <b>(?t=Date.now())</b> para garantir que o navegador sempre busque os dados mais recentes.</li>
</ul></p>

<p align="justify"><b>Bloco em Destaque:</b></p>

``` 
JavaScript

// Atualização automática via Fetch API
function atualizar() {
    fetch('previsao.json?nocache=' + Date.now())
        .then(res => res.json())
        .then(data => { /* Atualiza o gráfico e textos */ });
}
``` 
<p align="justify"><h4>6. O Servidor: nginx</h4></p>

<p align="justify">O servidor web que entrega a interface ao usuário.</p>

<p align="justify"><ul>
<li><b>Sincronização:</b> Como o arquivo <b>previsao.json</b> está mapeado via volume, o Nginx serve a versão atualizada instantaneamente assim que o modelo de IA termina o processamento.</li>
</ul></p>

<p align="justify"><b>Resumo do Fluxo:</b></p>
<p align="center"><b>Sensor → NiFi → Kafka → Modelo ML → Nginx → Gráfico</b></p>

![Texto Alternativo](https://github.com/rodfloripa/Projeto41/blob/main/previsoes.gif)

