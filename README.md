# Proyecto de Clasificación de Tweets en AWS

Este proyecto implementa una arquitectura en AWS para la clasificación de tweets utilizando procesamiento en batch y entrenamiento de modelos de machine learning con Amazon SageMaker, AWS Lambda, Amazon Redshift y Amazon S3.

## Descripción general

El objetivo de este proyecto es procesar tweets almacenados en un bucket de S3, transformarlos para entrenamiento e inferencia, entrenar un modelo de clasificación de sentimientos (-1: negativo, 0: neutro, 1: positivo), y almacenar los resultados en Amazon Redshift.

---

## Pasos para la implementación

### 1. Crear un rol con permisos adecuados

Crear un **IAM Role** con permisos para:

* **Amazon S3**
* **Amazon SageMaker**
* **Amazon Redshift**
* **AWS Secrets Manager**

Este rol debe tener permisos para leer y escribir en los recursos asociados.

---

### 2️. Crear un dominio en Amazon SageMaker

Crear un **SageMaker Domain** configurado con:

* Una **VPC** que permita la conexión entre:

  * SageMaker
  * Redshift
  * S3

Asegúrate de configurar correctamente los **subnets** y **security groups**.

---

### 3️. Crear un grupo de trabajo en Amazon Redshift

Crear un **workgroup** en Redshift con el nombre:

```
tweets-space3
```

---

### 4. Crear la tabla en Redshift

Ejecutar el script:

```
create-table.py
```

Este script se encarga de crear la tabla donde se almacenarán los tweets procesados.

---

### 5️. Configurar Lambda para procesar archivos nuevos

Configurar una **AWS Lambda** que se active cada vez que se cargue un nuevo archivo en el bucket de S3:

```
tweets-test-123
```

Esta Lambda ejecutará el script:

```
preprocess_modules.py
```

---

### 6️. Ejecutar script de preprocesamiento

El script `preprocess_modules.py`:

* Lee los datos crudos desde **S3**
* Los transforma para entrenamiento e inferencia
* Los almacena en **Redshift**

**Nota:** Para este ejercicio se asume que los tweets ya contienen la polaridad etiquetada y el objetivo es clasificarlos en:

* `-1` → Negativo
* `0`  → Neutro
* `1`  → Positivo

---

### 7️. Entrenar el modelo

Para entrenar un modelo, ejecutar:

```
train_modules.py
```

Este script:

* Carga los datos desde **Redshift**
* Utiliza un embedding de **GloVe para Twitter**:
  📎 [GloVe Twitter Embeddings](https://nlp.stanford.edu/projects/glove/)
* Prepara los datos
* Crea un **training job** en SageMaker
* Calcula métricas de desempeño
* Registra el modelo en **SageMaker Model Registry** para trazabilidad y versionamiento

---

### 8️. Realizar inferencias en batch

Usar el script:

```
inference_modules.py
```

Este script:

* Carga los datos desde **Redshift**
* Recupera la última versión del modelo entrenado desde el **Model Registry**
* Realiza la inferencia tras desplegar un endpoint temporal (o utilizando batch transform si se desea)
* Guarda los resultados en la tabla de Redshift

---

### 9️. Configurar Lambda para inferencias programadas

Configurar una **AWS Lambda** que se ejecute al menos una vez al día, para:

* Realizar inferencias con los tweets que se han ido almacenando
* Guardar los resultados de inferencia en la tabla de Redshift

---

##  Estructura de archivos

```
├── create-table.py
├── preprocess_modules.py
├── train_modules.py
└── inference_modules.py
```

---

##  Notas adicionales

* Este proyecto asume que la polaridad de los tweets viene predefinida para facilitar el proceso de entrenamiento.
* La arquitectura está pensada para un modelo de batch inference, no para inferencias en tiempo real.

---
