Upgrade a PVC from local-path/RWO to Longhorn/RWX.

Requires charon authentication. Uses rolling update strategy when the PVC is mounted by a Deployment.

**Input**: $ARGUMENTS — `<pvc-name> <namespace>` (e.g. `kord master`, `grafana-data master`)

## Procedure

### Step 1: Ensure Longhorn is installed

```bash
ssh kkord@<IP> "sudo kubectl get ns longhorn-system" || {
  # Install open-iscsi prerequisite on all nodes
  ssh kkord@<IP> "sudo apt-get install -y open-iscsi && sudo systemctl enable --now iscsid"
  # Install Longhorn
  ssh kkord@<IP> "sudo kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.7.3/deploy/longhorn.yaml"
  # Wait for rollout
  ssh kkord@<IP> "sudo kubectl -n longhorn-system rollout status deploy/longhorn-driver-deployer --timeout=120s"
  ssh kkord@<IP> "sudo kubectl -n longhorn-system rollout status daemonset/longhorn-manager --timeout=120s"
}
```

Verify the `longhorn` StorageClass uses `driver.longhorn.io` (not `rancher.io/local-path`):
```bash
ssh kkord@<IP> "sudo kubectl get sc longhorn -o jsonpath='{.provisioner}'"
```

### Step 2: Create new Longhorn RWX PVC

```bash
cat <<EOF | ssh kkord@<IP> "sudo kubectl apply -n <namespace> -f -"
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <name>-new
  labels:
    app: kord
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: longhorn
  resources:
    requests:
      storage: 20Gi
EOF

# Wait for PVC to bind
ssh kkord@<IP> "sudo kubectl wait --for=jsonpath='{.status.phase}'=Bound pvc/<name>-new -n <namespace> --timeout=120s"
```

### Step 3: Copy data via migration Job

Run a Job that mounts both old and new PVCs and copies data:

```bash
cat <<EOF | ssh kkord@<IP> "sudo kubectl apply -n <namespace> -f -"
apiVersion: batch/v1
kind: Job
metadata:
  name: kord-storage-migrate
spec:
  ttlSecondsAfterFinished: 300
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: alpine
          command: ["/bin/sh", "-c"]
          args:
            - |
              apk add --no-cache rsync
              echo "Copying data from old PVC to new PVC..."
              rsync -a --info=progress2 /old/ /new/
              echo "Verifying..."
              ls -la /new/
              echo "Migration copy complete."
          volumeMounts:
            - name: old-data
              mountPath: /old
              readOnly: true
            - name: new-data
              mountPath: /new
      volumes:
        - name: old-data
          persistentVolumeClaim:
            claimName: <name>
        - name: new-data
          persistentVolumeClaim:
            claimName: <name>-new
EOF

ssh kkord@<IP> "sudo kubectl wait -n <namespace> --for=condition=complete job/kord-storage-migrate --timeout=300s"
ssh kkord@<IP> "sudo kubectl logs job/kord-storage-migrate -n <namespace>"
```

Note: if old PVC is RWO, this Job may need to co-schedule on the same node.
For local-path RWO, multiple pods on the same node CAN mount the PVC.

### Step 4: Find and patch deployments using this PVC

Find all deployments referencing the PVC:

```bash
DEPLOYS=$(ssh kkord@<IP> "sudo kubectl get deploy -n <namespace> -o json" | \
  python3 -c "import json,sys; [print(d['metadata']['name']) for d in json.load(sys.stdin)['items'] for v in d['spec']['template']['spec'].get('volumes',[]) if v.get('persistentVolumeClaim',{}).get('claimName')=='<name>']")
```

For each deployment, find the volume index and patch it to use `<name>-new`:

```bash
for DEPLOY in $DEPLOYS; do
  # Find volume index (inspect the deployment to locate the correct path)
  ssh kkord@<IP> "sudo kubectl patch deploy/$DEPLOY -n <namespace> \
    --type=json -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/volumes/<idx>/persistentVolumeClaim/claimName\",\"value\":\"<name>-new\"}]'"
done
```

This triggers rolling updates. New pods start with `<name>-new`, old pods still have `<name>`.
Both run simultaneously during rollout.

```bash
for DEPLOY in $DEPLOYS; do
  ssh kkord@<IP> "sudo kubectl rollout status deploy/$DEPLOY -n <namespace> --timeout=300s"
done
```

### Step 5: Swap PVC names

Once all pods are running on `<name>-new`, rename it to `<name>`:

```bash
# Get the PV backing <name>-new
NEW_PV=$(ssh kkord@<IP> "sudo kubectl get pvc <name>-new -n <namespace> -o jsonpath='{.spec.volumeName}'")

# Set Retain policy on new PV so deleting the PVC doesn't delete data
ssh kkord@<IP> "sudo kubectl patch pv $NEW_PV -p '{\"spec\":{\"persistentVolumeReclaimPolicy\":\"Retain\"}}'"

# Scale all deployments to 0 briefly to release the PVCs
for DEPLOY in $DEPLOYS; do
  ssh kkord@<IP> "sudo kubectl scale deploy/$DEPLOY -n <namespace> --replicas=0"
done

# Delete <name>-new PVC (PV retained) and old <name> PVC
ssh kkord@<IP> "sudo kubectl delete pvc <name>-new -n <namespace>"
ssh kkord@<IP> "sudo kubectl delete pvc <name> -n <namespace>"

# Clear claimRef on the PV so it becomes Available
ssh kkord@<IP> "sudo kubectl patch pv $NEW_PV --type=json -p='[{\"op\":\"remove\",\"path\":\"/spec/claimRef\"}]'"

# Create final PVC with original name binding to the Longhorn PV
# Read original PVC size for the recreation
cat <<EOF | ssh kkord@<IP> "sudo kubectl apply -n <namespace> -f -"
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <name>
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: longhorn
  volumeName: $NEW_PV
  resources:
    requests:
      storage: <original-size>
EOF

# Wait for bind
ssh kkord@<IP> "sudo kubectl wait --for=jsonpath='{.status.phase}'=Bound pvc/<name> -n <namespace> --timeout=60s"

# Patch all deployments back to original PVC name and scale up
for DEPLOY in $DEPLOYS; do
  ssh kkord@<IP> "sudo kubectl patch deploy/$DEPLOY -n <namespace> \
    --type=json -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/volumes/<idx>/persistentVolumeClaim/claimName\",\"value\":\"<name>\"}]'"
  ssh kkord@<IP> "sudo kubectl scale deploy/$DEPLOY -n <namespace> --replicas=1"
done
for DEPLOY in $DEPLOYS; do
  ssh kkord@<IP> "sudo kubectl rollout status deploy/$DEPLOY -n <namespace> --timeout=300s"
done
```

Brief downtime during PVC swap (~30 seconds).

### Step 6: Report

Report:
- New PVC status (Bound, Longhorn, RWX)
- All deployment pod statuses
- Old PV status (retained as backup on the node)

## Notes

- Rolling update (maxSurge:1, maxUnavailable:0) ensures near-zero-downtime during step 4
- Brief downtime (~30s) during PVC swap in step 5 is unavoidable
- Old hostPath PV is retained (Retain policy) as backup — clean up via migrate-cleanup
- Longhorn requires `open-iscsi` on all Linux nodes — macOS/Docker VMs cannot run Longhorn
