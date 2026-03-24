Prometheus & Grafana Stack
=====

The compose file defines a stack with two services prometheus and grafana. When deploying the stack, docker compose maps port the default ports for each service to the equivalent ports on the host in order to inspect easier the web interface of each service. Make sure the ports 9090 and 3000 on the host are not already in use.

```
$ docker compose up -d
Creating network "prometheus-grafana_grafana" with driver "bridge"
Creating volume "prometheus-grafana_grafana-data" with default driver
Creating volume "prometheus-grafana_prometheus-data" with default driver
...
Creating prometheus ... done
Creating grafana    ... done
```