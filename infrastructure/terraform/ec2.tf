# ─────────────────────────────
# EC2 — k3s Single Node
# Free tier: t2.micro (750h/month free)
# ─────────────────────────────

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }
}

resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-key"
  public_key = var.ssh_public_key
}

resource "aws_instance" "k3s" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type   # t2.micro for free tier
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.k3s.id]
  key_name               = aws_key_pair.deployer.key_name

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  # Install k3s + ArgoCD automatically on first boot
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Install k3s (lightweight Kubernetes)
    curl -sfL https://get.k3s.io | sh -

    # Wait for k3s to be ready
    sleep 30
    export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

    # Install ArgoCD
    kubectl create namespace argocd
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

    # Expose ArgoCD on NodePort 30080
    kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort", "ports": [{"port": 443, "targetPort": 8080, "nodePort": 30080}]}}'

    # Install Helm
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

    echo "✅ k3s + ArgoCD + Helm installed!"
  EOF

  tags = {
    Name = "${var.project_name}-k3s"
  }
}

output "k3s_public_ip" {
  value       = aws_instance.k3s.public_ip
  description = "SSH: ssh ubuntu@<this_ip> | ArgoCD: https://<this_ip>:30080"
}
