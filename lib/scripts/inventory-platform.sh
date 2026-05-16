#!/usr/bin/env bash
set -euo pipefail

host="${1:-ottawa-server}"

run() {
  local title="$1"
  shift
  printf '\n===== %s =====\n' "$title"
  "$@" || true
}

remote() {
  ssh "$host" "$@"
}

run "host identity" remote 'hostname; whoami; uname -a; cat /etc/os-release | sed -n "1,12p"'
run "host tools" remote 'for x in kubectl k3s docker nerdctl ctr crictl tailscale rclone; do command -v "$x" || true; done'
run "host filesystems" remote 'df -hT; echo; lsblk -f'
run "host mounts" remote 'findmnt -R /var/lib/rancher /var/lib/docker /var/snap/docker /mnt/hdd /srv 2>/dev/null || true'
run "tailscale status" remote 'tailscale status 2>/dev/null | sed -n "1,160p"; echo; tailscale ip -4 2>/dev/null || true; echo; tailscale serve status 2>/dev/null || true'
run "tailscale json self" remote 'tailscale status --json 2>/dev/null | python3 -m json.tool 2>/dev/null | sed -n "1,220p" || true'
run "routing" remote 'ip route | sed -n "1,160p"'

run "kubernetes nodes" remote 'sudo kubectl get nodes -o wide'
run "kubernetes namespaces" remote 'sudo kubectl get ns'
run "kubernetes storageclasses" remote 'sudo kubectl get storageclass -o wide'
run "kubernetes pvs" remote 'sudo kubectl get pv -o wide'
run "kubernetes pvcs" remote 'sudo kubectl get pvc -A -o wide'
run "kubernetes pods" remote 'sudo kubectl get pods -A -o wide'
run "kubernetes services" remote 'sudo kubectl get svc -A -o wide'
run "kubernetes ingress" remote 'sudo kubectl get ingress -A -o wide 2>/dev/null || true'
run "kubernetes workloads" remote 'sudo kubectl get deploy,statefulset,daemonset -A -o wide'
run "kubernetes jobs" remote 'sudo kubectl get cronjob,job -A -o wide 2>/dev/null || true'
run "recent events" remote 'sudo kubectl get events -A --sort-by=.lastTimestamp | tail -120'

run "longhorn volumes" remote 'sudo kubectl -n longhorn-system get volumes.longhorn.io -o wide 2>/dev/null || true'
run "longhorn nodes" remote 'sudo kubectl -n longhorn-system get nodes.longhorn.io -o wide 2>/dev/null || true'

run "workstation deployment" remote 'sudo kubectl -n master get deploy workstation -o yaml 2>/dev/null | sed -n "1,260p"'
run "registry deployment and pvc" remote 'sudo kubectl -n registry get deploy registry -o yaml 2>/dev/null; echo; sudo kubectl -n registry get pvc registry-data -o yaml 2>/dev/null'
run "minio deployment and pvc" remote 'sudo kubectl -n gateway get deploy minio -o yaml 2>/dev/null; echo; sudo kubectl -n gateway get pvc minio-data -o yaml 2>/dev/null'
run "augur deployments and pvc" remote 'sudo kubectl -n augur get deploy -o wide 2>/dev/null; echo; sudo kubectl -n augur get pvc augur-state -o yaml 2>/dev/null'

run "docker summary" remote 'docker info 2>/dev/null | sed -n "1,120p"; echo; docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" 2>/dev/null || true'
