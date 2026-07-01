# Azure Architecture

## Objetivo

Este documento describe cómo podría evolucionar el proyecto local hacia una arquitectura en Azure.

La versión actual del proyecto funciona de forma local usando Python, PySpark, PostgreSQL y Power BI. La arquitectura propuesta busca adaptar ese flujo a servicios cloud, manteniendo la lógica de capas Bronze, Silver y Gold.

---

## Arquitectura propuesta

```text
Archivos fuente
    ↓
Azure Data Lake Storage Gen2 - Landing
    ↓
Azure Data Factory
    ↓
Azure Data Lake Storage Gen2 - Bronze
    ↓
Azure Databricks / PySpark
    ↓
Azure Data Lake Storage Gen2 - Silver
    ↓
Azure Databricks / PySpark
    ↓
Azure Data Lake Storage Gen2 - Gold
    ↓
Validaciones de calidad
    ↓
Azure SQL Database
    ↓
Power BI