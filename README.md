# Práctica Formativa Integradora
## Consolidación de Almacenamiento, Integridad del Dato y Toma de Contacto con HDFS

**Módulos:** 5075 — Integridad y calidad del dato · 5074 — Almacenamiento distribuido con Hadoop

---

## 1. Integridad del dato — Módulo 5075

El primer bloque de la práctica consistió en verificar la integridad del fichero original `telemetria_envios.csv` mediante el algoritmo criptográfico SHA-256 y realizar un proceso de saneamiento de los datos utilizando Python.

Se calculó la huella digital del fichero original y, posteriormente, se generó `telemetria_limpia.csv`, eliminando registros duplicados e inconsistentes y aplicando controles de calidad sobre los campos relevantes.

### Resultados SHA-256

| Archivo | SHA-256 |
|---|---|
| `telemetria_envios.csv` | `317f5047ddc0407b36fe4b8af54b919e5a2f815555c5c1b0c176cff4e0df0181` |
| `telemetria_limpia.csv` | `43e120cd233ebf05d410c8e2911b021885b5a708d3b16fabca4c69431323a8b6` |

Las huellas son diferentes porque el fichero limpio contiene modificaciones respecto al original. SHA-256 permite comprobar la integridad de cada archivo: cualquier cambio en su contenido produce una huella diferente.

## 2. Despliegue y HDFS — Módulo 5074

Para realizar la práctica se desplegó un entorno de Apache Hadoop 3.4.0 mediante Docker Desktop. Se utilizó un único contenedor, denominado `hadoop-lab`, con los servicios de Hadoop configurados para funcionar en el mismo entorno.

### Verificación de servicios

Se utilizó el comando `jps` para comprobar que los cuatro procesos principales estaban activos:

- **NameNode:** administra los metadatos y el espacio de nombres de HDFS.
- **DataNode:** almacena los bloques de datos.
- **ResourceManager:** gestiona los recursos de YARN.
- **NodeManager:** administra los recursos del nodo de ejecución.

La comprobación confirmó la presencia de los cuatro procesos.

### Puertos publicados

| Puerto | Servicio |
|---|---|
| `9870` | Interfaz web del NameNode |
| `8088` | Interfaz web del ResourceManager |
| `9864` | Interfaz HTTP del DataNode |
| `8042` | Interfaz web del NodeManager |

### Ingesta de datos en HDFS

Los archivos CSV se encontraban en la carpeta local `datos`, compartida con el contenedor mediante `/workspace`.

Se creó el directorio de destino en HDFS:

```bash
hdfs dfs -mkdir -p /user/hadoop/datos
```

A continuación, se copiaron los dos archivos:

```bash
hdfs dfs -put /workspace/telemetria_envios.csv /workspace/telemetria_limpia.csv /user/hadoop/datos/
```

Se comprobó su presencia mediante:

```bash
hdfs dfs -ls /user/hadoop/datos
```

El listado confirmó los dos archivos:

- `telemetria_envios.csv` — 37.424 bytes.
- `telemetria_limpia.csv` — 34.157 bytes.

### Comprobación de bloques e integridad

Para auditar el almacenamiento se ejecutó:

```bash
hdfs fsck /user/hadoop/datos -files -blocks -locations
```

El análisis confirmó que ambos archivos estaban almacenados correctamente, con un bloque cada uno y una réplica por bloque.

El resultado final fue:

```text
Status: HEALTHY
Missing blocks: 0
Corrupt blocks: 0
Missing replicas: 0
```

Por tanto, la comprobación de HDFS no detectó bloques perdidos ni corruptos.

## 3. Análisis crítico: tolerancia a fallos en HDFS

HDFS está diseñado para almacenar grandes volúmenes de información distribuyendo los archivos en bloques entre distintos DataNodes. En un clúster de producción, cada bloque se almacena con un determinado factor de replicación. Esto significa que pueden existir varias copias del mismo bloque en diferentes nodos, de modo que la información no dependa de un único equipo físico.

Si un DataNode falla o se apaga, el NameNode detecta que ha dejado de enviar señales periódicas (*heartbeats*) y lo considera no disponible. Los bloques que únicamente estaban accesibles a través de ese nodo pueden seguir estando disponibles mediante las copias almacenadas en otros DataNodes. De esta manera, los clientes pueden continuar accediendo a los datos sin depender del nodo que ha fallado.

Además, el NameNode supervisa el estado de los bloques y detecta cuándo su número de réplicas disponibles queda por debajo del factor de replicación configurado. Cuando hay suficientes nodos y espacio disponibles, HDFS puede generar nuevas réplicas para recuperar el nivel de redundancia establecido. Así, la distribución de bloques, la replicación y la supervisión del NameNode permiten ofrecer tolerancia a fallos y reducir el riesgo de pérdida de información. Esta protección depende de que existan copias disponibles y no sustituye a las copias de seguridad frente a cualquier tipo de desastre.

## 4. Evidencias gráficas

Las capturas realizadas durante la práctica se encuentran en la carpeta `/evidencias` del repositorio.

| Evidencia | Descripción |
|---|---|
| [01_hashes_sha256.png](evidencias/01_hashes_sha256.png) | Cálculo de las huellas SHA-256 de los archivos original y saneado. |
| [02_jps_servicios.png](evidencias/02_jps_servicios.png) | Verificación de los cuatro procesos Hadoop mediante `jps`. |
| [03_hdfs_comandos_fsck.png](evidencias/03_hdfs_comandos_fsck.png) | Ingesta, listado de archivos y auditoría de bloques mediante `hdfs fsck`. |
| [04_webui_hdfs_browse.png](evidencias/04_webui_hdfs_browse.png) | Exploración de los archivos almacenados desde la interfaz web del NameNode. |

---

**Conclusión**

La práctica ha permitido realizar un proceso completo desde la verificación y depuración de los datos en el entorno local hasta su almacenamiento y comprobación en HDFS. También se ha verificado el funcionamiento de los servicios principales de Hadoop y se ha comprobado mediante `fsck` que los archivos almacenados no presentan bloques perdidos ni corruptos.
