# Traefik Configuration for PyNewsServer

This document describes the Traefik reverse proxy setup for the PyNewsServer project.

## Overview

Traefik is configured as a reverse proxy to route traffic to the different services in the PyNewsServer stack:

- **Main API**: Available at `http://localhost` or `http://api.localhost`
- **ScanAPI Reports**: Available at `http://reports.localhost`
- **Traefik Dashboard**: Available at `http://traefik.localhost` or `http://localhost:8080`

## Services and Ports

### Traefik (Reverse Proxy)
- **Container**: `pynews-traefik`
- **HTTP Port**: 80
- **HTTPS Port**: 443 (with Let's Encrypt support)
- **Dashboard Port**: 8080
- **Dashboard URL**: `http://traefik.localhost` or `http://localhost:8080`

### PyNews API
- **Container**: `pynews-server`
- **Internal Port**: 8000
- **External Access**: `http://localhost` or `http://api.localhost`
- **Healthcheck**: Available at `/api/healthcheck`

### ScanAPI Report Viewer
- **Container**: `scanapi-report-viewer`
- **Internal Port**: 80
- **External Access**: `http://reports.localhost`

## Configuration Files

- `traefik/traefik.yml`: Static configuration for Traefik
- `traefik/dynamic.yml`: Dynamic configuration for additional routing and middleware
- `traefik/acme.json`: Let's Encrypt certificate storage (auto-generated)

## Docker Labels

Services are configured using Docker labels for automatic service discovery:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.<service>.rule=Host(`<hostname>`)"
  - "traefik.http.routers.<service>.entrypoints=web"
  - "traefik.http.services.<service>.loadbalancer.server.port=<port>"
```

## SSL/TLS Support

Traefik is configured with Let's Encrypt for automatic SSL certificate generation. To enable HTTPS:

1. Update the router labels to use the `websecure` entrypoint
2. Add certificate resolver configuration
3. Configure your domain to point to your server

Example for HTTPS:
```yaml
labels:
  - "traefik.http.routers.api-secure.rule=Host(`yourdomain.com`)"
  - "traefik.http.routers.api-secure.entrypoints=websecure"
  - "traefik.http.routers.api-secure.tls.certresolver=letsencrypt"
```

## Local Development

For local development, add the following entries to your `/etc/hosts` file:

```
127.0.0.1 localhost
127.0.0.1 api.localhost
127.0.0.1 reports.localhost
127.0.0.1 traefik.localhost
```

## Starting the Services

```bash
# Start all services including Traefik
docker-compose up -d

# View logs
docker-compose logs traefik

# Stop all services
docker-compose down
```

## Monitoring

- **Traefik Dashboard**: Monitor routing, services, and middleware at `http://traefik.localhost`
- **Service Health**: Check service status through the dashboard
- **Logs**: Access logs are enabled for debugging

## Security Features

- Rate limiting middleware
- CORS configuration
- Security headers
- Docker socket protection (read-only access)

## Troubleshooting

1. **Service not accessible**: Check that the service has the correct Traefik labels
2. **SSL issues**: Ensure the `acme.json` file has correct permissions (600)
3. **Network issues**: Verify all services are on the `pynews-network`
4. **DNS resolution**: Add hostnames to `/etc/hosts` for local development