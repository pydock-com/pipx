# !/usr/bin/env python3

import os
import subprocess
import sys


def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def is_docker_installed():
    return run_command("docker --version")


def install_docker():
    print("Instalowanie Dockera...")

    # Wykryj dystrybucję
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            os_release = f.read()
        if "ID=ubuntu" in os_release or "ID=debian" in os_release:
            return run_command("""
                sudo apt-get update && 
                sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common &&
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - &&
                sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" &&
                sudo apt-get update &&
                sudo apt-get install -y docker-ce docker-ce-cli containerd.io
            """)
        elif "ID=fedora" in os_release or "ID=centos" in os_release or "ID=rhel" in os_release:
            return run_command("""
                sudo dnf -y install dnf-plugins-core &&
                sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo &&
                sudo dnf install -y docker-ce docker-ce-cli containerd.io
            """)
        elif "ID=arch" in os_release:
            return run_command("sudo pacman -S --noconfirm docker")

    print("Nie udało się automatycznie zainstalować Dockera. Proszę zainstalować ręcznie.")
    return False


def run_snapd_in_docker(snap_app):
    print(f"Uruchamianie {snap_app} w kontenerze Docker...")
    command = f"""
    docker run -it --rm \
        -v /tmp:/tmp \
        -v /run:/run \
        --privileged \
        ubuntu:latest \
        /bin/bash -c "apt update && apt install -y snapd && snap install {snap_app} && {snap_app}"
    """
    return run_command(command)


def main():
    if not is_docker_installed():
        if not install_docker():
            print("Nie udało się zainstalować Dockera. Proszę zainstalować ręcznie i uruchomić skrypt ponownie.")
            sys.exit(1)

    if not run_command("sudo systemctl start docker"):
        print("Nie udało się uruchomić usługi Docker. Upewnij się, że masz uprawnienia sudo.")
        sys.exit(1)

    snap_app = input("Podaj nazwę aplikacji Snap do uruchomienia: ")
    if run_snapd_in_docker(snap_app):
        print(f"Aplikacja {snap_app} została uruchomiona pomyślnie.")
    else:
        print(f"Wystąpił błąd podczas uruchamiania aplikacji {snap_app}.")


if __name__ == "__main__":
    main()