# Deploying the Three-Tier App to Kubernetes

## How the tiers communicate

Kubernetes gives every Service a DNS name equal to its `metadata.name` (within the namespace). This app relies on that:

- **Frontend → Backend**: The frontend's Nginx config (baked into its image) proxies `/api/*` to `http://backend:5000/api/`. This works because the backend Service is named `backend`.
- **Backend → Database**: The backend's `DB_HOST` env var is set to `db`. This works because the MySQL Service is named `db`.

So as long as you don't rename the Services in the manifests, everything resolves automatically — no IP addresses or hardcoding needed.

```
Browser --> frontend Service (NodePort 30080) --> frontend Pods --> backend Service (5000) --> backend Pods --> db Service (3306) --> db Pod (MySQL)
```

## 1. Build the images

From the project root (one level above `k8s/`):

```bash
docker build -t three-tier-frontend:latest ./frontend
docker build -t three-tier-backend:latest ./backend
```

## 2. Make the images available to your cluster

Kubernetes doesn't see your local Docker images by default — how you fix that depends on your cluster:

**minikube:**
```bash
minikube image load three-tier-frontend:latest
minikube image load three-tier-backend:latest
```

**kind:**
```bash
kind load docker-image three-tier-frontend:latest
kind load docker-image three-tier-backend:latest
```

**Real cluster (EKS/GKE/AKS/etc.):**
Push to a registry instead, then update the `image:` fields in
`k8s/06-backend-deployment.yaml` and `k8s/08-frontend-deployment.yaml`:
```bash
docker tag three-tier-backend:latest <your-registry>/three-tier-backend:latest
docker push <your-registry>/three-tier-backend:latest
# repeat for frontend, then edit the image: fields to match
```

## 3. Deploy

Apply the manifests in order (the numeric prefixes handle dependency order):

```bash
kubectl apply -f k8s/
```

Watch things come up:

```bash
kubectl get pods -n three-tier-app -w
```

Wait until all pods show `Running` / `1/1` or `2/2` Ready. MySQL takes the longest to become ready.

## 4. Access the app

**minikube:**
```bash
minikube service frontend -n three-tier-app --url
```

**kind / bare metal / on-prem:**
```bash
kubectl get nodes -o wide   # get a node's internal/external IP
# then browse to http://<node-ip>:30080
```

**Or, for a quick local test without NodePort:**
```bash
kubectl port-forward -n three-tier-app svc/frontend 8080:80
```
Then open `http://localhost:8080`.

## 5. Verify connectivity between tiers

```bash
# Check backend can see the DB
kubectl logs -n three-tier-app deploy/backend

# Check frontend can reach backend (exec into a frontend pod)
kubectl exec -it -n three-tier-app deploy/frontend -- wget -qO- http://backend:5000/api/health
```

## 6. Clean up

```bash
kubectl delete -f k8s/
```

Note: `kubectl delete -f k8s/` will also delete the PVC only if it's included and you're deleting the whole directory — MySQL data will be lost. Omit `03-mysql-pvc.yaml` from the delete if you want to keep the data.

## Manifest overview

| File | Purpose |
|---|---|
| `00-namespace.yaml` | Creates the `three-tier-app` namespace |
| `01-mysql-secret.yaml` | DB credentials |
| `02-mysql-configmap.yaml` | Table-creation SQL run on first MySQL startup |
| `03-mysql-pvc.yaml` | Persistent storage for MySQL data |
| `04-mysql-deployment.yaml` | MySQL pod |
| `05-mysql-service.yaml` | Headless Service named `db` |
| `06-backend-deployment.yaml` | Flask API pods (2 replicas) |
| `07-backend-service.yaml` | ClusterIP Service named `backend` |
| `08-frontend-deployment.yaml` | Nginx pods (2 replicas) |
| `09-frontend-service.yaml` | NodePort Service exposing the app externally |

## Notes / next steps

- Credentials are in plaintext in `01-mysql-secret.yaml` for simplicity — for anything beyond local testing, use a real secrets manager (Sealed Secrets, External Secrets Operator, Vault, etc.) instead of checking secrets into git.
- For production traffic, swap the frontend's NodePort for an **Ingress** + a proper Ingress controller (nginx-ingress, ALB, etc.) so you get a real hostname and TLS.
- If you want zero-downtime rolling updates on the backend, the Deployment already defaults to `RollingUpdate` strategy — just update the image tag and re-apply.
