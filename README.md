# PTA Server

## Overview

The **PTA Server** is a file transfer protocol built to communicate over TCP. This guide will help you set up and run the server and client for proper functionality.

## How to Get Started

### 1. Run the PTA Server

To start the PTA server, run the script `pta_server_v1.0.py`. You must specify the **IP address**, **Port**, and **User** as arguments.

#### Example Command:

```bash
python .\pta-client.py localhost 11550 user2
```

In this example:
- `localhost` is the IP address where the server is hosted.
- `11550` is the port where the server listens.
- `user2` is the client username.

Make sure that the user is listed in the valid users' file on the server for successful authentication.

## Requirements

- **Python 3.x** installed on your system.
- Ensure the **valid users list** and **server files directory** are properly configured on the server.

## Troubleshooting

- If the server does not start, verify that the IP address and port are available.
- Make sure the client is a valid user listed on the server.
- For connection issues, confirm that the firewall settings allow communication on the specified port.

For further help, check the log output on the server terminal for detailed error messages.
