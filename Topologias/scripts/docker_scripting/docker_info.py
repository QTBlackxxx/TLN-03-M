import docker

client = docker.from_env()

for contenedor in client.containers.list():
    labels = contenedor.labels

    if "clab-node-name" in labels:
        print(contenedor.name)