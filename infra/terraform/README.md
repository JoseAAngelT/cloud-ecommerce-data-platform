# Terraform Infrastructure

## Objetivo

Esta carpeta contiene una base de infraestructura como código para llevar el proyecto a Azure.

La infraestructura propuesta acompaña la arquitectura documentada en `docs/azure_architecture.md`.

## Recursos definidos

- Resource Group.
- Storage Account con Data Lake Gen2.
- Contenedores para Landing, Bronze, Silver y Gold.
- Azure Key Vault.
- Azure SQL Server.
- Azure SQL Database.
- Azure Data Factory.

## Estado actual

Esta configuración funciona como base inicial.

No es obligatorio ejecutar `terraform apply` para usar la versión local del proyecto.

## Comandos principales

Inicializar Terraform:

```powershell
terraform init