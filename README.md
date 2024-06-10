## Overview

AstraMax is originally a 3 days hack project for the purpose of demoing what's possible with those SOTA low latency multimodal LLMs. I was having fun building this and decided to continue work on it in my spare time.

In a nutshell, AstraMax is a glass based personal AI assistant built on top of raspberry pi and low latency multimodal LLMs. The assistant not only can see the world and chat with you, it can also help you take actions on your computer, helping you write code by just looking at your screen or generating images by looking at real world objects.

The overall architecture looks like this:

![AstraMax overall architecture](https://lh3.googleusercontent.com/drive-viewer/AKGpihbclnAaku8hmuovERdyKWrm0ALV4K9VQHNMl2KwFd4jV1_rCI6Zr9k8XVkzvz6gxowL2_gDggN29I28j0KHyDrvglIS8_iGIQ=s1600-rw-v1)

It has three major building blocks:

- Hardware - Glass: raspberry pi and pi camera based hardware that can attach to normal glass
- Message relay service: provide message streaming to desktop agent
- Desktop agent: desktop application based on Electron, consuming the message stream and generate action to take on your computer

The current implementation relies on Google Gemini 1.5 Flash, Speech2Text/Text2Speech and ImageGen2 model through Google cloud vertex AI, but it should be easily replicable with other models.

## Folder structure

### pi-ware

PI firmware, the main software running on Raspberry PI

### hardware

Some 3D printable parts that are used to attach Raspberry PI and PI Camera modules on the regular glass.

### service

Message relay service providing HTTP API endpoint for create message and serve message streaming

### desktop-app

Electron based desktop application

### deployment

Environment related configuration file(example only, no actual environment files), db script, docker compose file and other scripts to make the development and test easier.

## Demo

I recorded a demo [here](https://youtu.be/qzpQp0Lygjg).

## Authors

- Ke(Edwin) Huang [@hkbarton](https://x.com/hkbarton1983)
