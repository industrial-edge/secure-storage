# Installation

- [Installation](#installation)
  - [Build application](#build-application)
    - [Cloning image](#cloning-image)
    - [Build docker image](#build-docker-image)
  - [Upload Secure Storage App to the Industrial Edge Managment](#upload-secure-storage-app-to-the-industrial-edge-managment)
    - [Connect your Industrial Edge App Publisher](#connect-your-industrial-edge-app-publisher)
    - [Upload Secure Storage App using the Industrial Edge App Publisher](#upload-secure-storage-app-using-the-industrial-edge-app-publisher)
  - [Deploying of App](#deploying-of-app)

## Build application

### Cloning image

- Clone or Download the source code to your engineering VM

### Build docker image

- Open console in the source code folder
- Use command `docker compose build` to create the docker image.
- This docker image can now be used to build you app with the Industrial Edge App Publisher
- `docker images | grep secure-storage-app` can be used to check for the images
- You should get a result similiar to this:

  ![deploy VFC](./graphics/docker_images_securestorageapp.png)

## Upload Secure Storage App to the Industrial Edge Managment

Please find below a short description how to publish your application in your IEM.

For more detailed information please see the section for [uploading apps to the IEM](https://github.com/industrial-edge/upload-app-to-iem).

### Connect your Industrial Edge App Publisher

- Connect your Industrial Edge App Publisher to your docker engine
- Connect your Industrial Edge App Publisher to your Industrial Edge Managment System

### Upload Secure Storage App using the Industrial Edge App Publisher

- Create a new application using the Industrial Publisher
- Add a new app version
- Import the [docker-compose](../docker-compose.yml) file using the **Import YAML** button
- The warning `Build (services >> scanner-service) is not supported` can be ignored
- **Start Upload** to transfer the app to Industrial Edge Managment
- Further information about using the Industrial Edge App Publisher can be found in the [IE Hub](https://iehub.eu1.edge.siemens.cloud/documents/appPublisher/en/start.html)

## Deploying of App

Select the Uploaded version of the Application and Install it to the desired Industrial Edge Device.
