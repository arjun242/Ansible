subscription_name=$1

az login --identity --username ec4d7eec-bf83-465d-a693-8c5e98bd84bd
az account set --subscription $1
az feature register --namespace Microsoft.Compute --name EncryptionAtHost
az provider register -n Microsoft.Compute