# README

# Terraform

## Overview

This Terraform module is responsible for provisioning the infrastructure required to support the ETL pipeline. I uses Azure as a provider.

It manages the following components:

- Resource group
- Azure Database for PostgreSQL flexible server

## Configuration

Copy `terraform_tfvars_template.txt` to `terraform.tfvars` and set required variables there.

## Getting Started

```
cd terraform
terraform init
terraform plan
terraform apply
```
