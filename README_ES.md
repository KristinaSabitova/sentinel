# SENTINEL
### Análisis de Reputación de IPs e Inteligencia de Amenazas — Kit de Reconocimiento OSINT

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/Licencia-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Estado-Activo-brightgreen?style=flat-square)
![Platform](https://img.shields.io/badge/Plataforma-macOS%20%7C%20Linux-lightgrey?style=flat-square)
![OSINT](https://img.shields.io/badge/Tipo-OSINT-blueviolet?style=flat-square)

> 🛡️ Parte de la **DOMINI Suite** — framework de reconocimiento OSINT pasivo de dos herramientas.  
> SENTINEL analiza IPs. [DOMINUS](https://github.com/youruser/dominus) analiza dominios.  
> Juntas mapean la superficie de ataque completa de cualquier objetivo.

---

## ¿Qué es SENTINEL?

SENTINEL es una herramienta de inteligencia de amenazas OSINT pasivo orientada a **direcciones IP**. Dada una IP, agrega datos de reputación, geolocalización, historial de abuso, feeds de amenazas activas, contexto de proveedor cloud y detección de Tor/VPN — luego calcula un **Threat Score de 0 a 100** transparente y genera un informe HTML standalone con mapa interactivo de geolocalización.

Donde [DOMINUS](https://github.com/youruser/dominus) pregunta *"¿qué tan expuesta está esta organización?"*, **SENTINEL pregunta "¿es esta IP una amenaza?"**

---

## ¿Qué encuentra?

| Fase | Datos recopilados |
|------|------------------|
| **Geolocalización** | País, ciudad, coordenadas, ASN, ISP, organización — via ip-api.com (sin key) |
| **Abuso** | Total de reportes, confidence score, categorías de ataque, fecha del último reporte — via AbuseIPDB |
| **Feeds de Amenazas** | Presencia en pulsos de AlienVault OTX, tipos de indicadores, asociaciones con actores de amenaza |
| **Puertos** | Servicios TCP abiertos y banners de versión via nmap |
| **Detección Cloud** | Identifica si la IP pertenece a AWS, Azure, GCP o Cloudflare usando rangos de IPs públicos |
| **Detección Tor** | Consulta en tiempo real contra dan.me.uk/torlist — detecta nodos de salida Tor activos al instante |

---

## ¿Qué significa el Threat Score?

Cada hallazgo suma puntos ponderados a un **Threat Score de 0 a 100**:

| Puntuación | Nivel | Qué significa |
|------------|-------|---------------|
| 0–25 | 🟢 Bajo | IP limpia, sin historial de abuso, proveedor legítimo |
| 26–50 | 🟡 Medio | Algunos reportes de abuso, o Tor/VPN detectado |
| 51–75 | 🔴 Alto | Múltiples categorías de abuso, aparece en feeds de amenazas |
| 76–100 | 🔥 Crítico | IP de atacante activo, abuso de alta confianza, múltiples hits en feeds |

**Cada punto está explicado.** El informe muestra exactamente qué hallazgo contribuyó qué puntuación.

---

## ¿Para qué sirve?

**Analistas SOC** — para triar alertas: cuando una IP aparece en los logs, SENTINEL dice en segundos si es una amenaza conocida, un nodo Tor, un proveedor cloud o una dirección residencial limpia.

**Respondedores de incidentes** — durante investigaciones activas para perfilar infraestructura atacante: de dónde viene, qué proveedor usa, si emplea anonimización, si otros la han reportado.

**Pentesters** — para verificar que su propia infraestructura no está marcada antes de un engagement.

**Threat hunters** — para enriquecer indicadores de compromiso (IOCs) convirtiendo una IP cruda de un alert en un perfil de amenaza completo.

**Casos de uso reales:**

- Una IP aparece repetidamente en tus logs SSH — ¿es un escáner, un bot o un atacante dirigido?
- Recibes un email de phishing — ¿qué revela la IP del remitente sobre la infraestructura?
- Un cliente reporta tráfico sospechoso — SENTINEL perfila la fuente en segundos
- Estás construyendo una blocklist — SENTINEL valida qué IPs son genuinamente maliciosas

---

## Entendiendo los resultados: ejemplo real

**Objetivo: 185.220.101.1**

```
Threat Score  : 32 / 100 — MEDIO
País          : Alemania · Ciudad de Brandeburgo
ASN           : AS60729 Stiftung Erneuerbare Freiheit
Nodo Tor      : ✓ NODO DE SALIDA ACTIVO DETECTADO
Reportes abuso: 143 (SSH brute force, port scanning, DDoS)
Cloud         : No es proveedor cloud conocido
Puertos       : 80, 443
```

**Qué significa:** Esta IP es un nodo de salida Tor — miles de usuarios diferentes enrutan tráfico a través de ella de forma anónima. Los 143 reportes no son necesariamente de un solo atacante; reflejan la actividad acumulada de todos los que han usado este nodo maliciosamente. Bloquear esta IP aislada ofrece protección limitada porque el atacante puede cambiar de nodo trivialmente.

**Recomendaciones de SENTINEL en este caso:**
- Bloquear el rango completo de nodos Tor, no solo esta IP
- Implementar MFA en servicios expuestos — el brute force via Tor es resistente a bloqueos por IP
- Añadir al SIEM para correlación histórica
- Reportar a AbuseIPDB para contribuir a la base de datos comunitaria

Esta es la diferencia entre una simple consulta de IP y **inteligencia de amenazas accionable**.

---

## SENTINEL + DOMINUS: la imagen completa

```bash
# Paso 1: DOMINUS mapea el dominio y extrae IPs
python dominus.py evolve.es --only dns
# Registros DNS revelan: XX.XXX.XXX.XXX y XX.XX.XXX.XXX

# Paso 2: SENTINEL perfila cada IP
python sentinel.py XX.XXX.XXX.XXX
# → OVH/Wetopi · España · Threat Score 2/100 · Limpia

python sentinel.py XX.XX.XXX.XXX
# → OVH/Wetopi · Países Bajos · Threat Score 2/100 · Limpia
```

**Conclusión combinada:** ejemplo.es tiene problemas de autenticación de email a nivel DNS (DMARC p=none, SPF soft-fail) pero su infraestructura subyacente es limpia, alojada en Europa, sin historial de abuso. El riesgo está en la configuración, no en los servidores.

> 🔗 Ver [DOMINUS](https://github.com/youruser/dominus) para reconocimiento a nivel de dominio.

---

## El informe

Un único archivo `.html`. Ábrelo en cualquier navegador. Envíaselo a quien quieras.

- IP en tipografía prominente con bandera del país y ASN
- Anillo SVG de Threat Score animado con acento cian
- **Mapa interactivo Leaflet.js** con marcador pulsante en la ubicación exacta de la IP
- Banner rojo animado cuando se detecta Tor/VPN
- Timeline de categorías de ataque con barras proporcionales
- Cards de contexto cloud con iconos
- Tabla de puertos con colores por severidad
- Recomendaciones accionables numeradas con badges de prioridad
- Datos raw por fase colapsables
- **Botón Exportar JSON** — descarga datos estructurados directamente desde el HTML
- **Selector de idioma: 🇪🇸 Español / 🇷🇺 Ruso** — cambio instantáneo sin recargar
- Completamente standalone — todo CSS y JS inline

---

## Instalación

```bash
git clone https://github.com/youruser/sentinel.git
cd sentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install nmap        # macOS
sudo apt install nmap    # Linux
```

**API keys (opcionales pero recomendadas):**

```bash
cp .env.example .env
# Edita .env y añade:
# ABUSEIPDB_KEY=tu_key    → tier gratuito: 1000 checks/día en abuseipdb.com
# OTX_KEY=tu_key          → gratuito, ilimitado en otx.alienvault.com
```

SENTINEL funciona sin ellas — esas fases se omiten con elegancia y quedan marcadas en el informe.

---

## Uso

```bash
# Escaneo completo
.venv/bin/python sentinel.py 185.220.101.1

# Sin escaneo de puertos (más rápido)
.venv/bin/python sentinel.py 185.220.101.1 --skip ports

# Solo fases específicas
.venv/bin/python sentinel.py 185.220.101.1 --only geo abuse tor

# Escaneo completo + exportación JSON
.venv/bin/python sentinel.py 185.220.101.1 --json
```

---

## Stack tecnológico

| Librería | Uso |
|----------|-----|
| `requests` | ip-api.com, AbuseIPDB, OTX, lista Tor, rangos cloud |
| `python-nmap` | Escaneo de puertos |
| `jinja2` | Generación del informe HTML |
| `rich` | Output visual en terminal |
| Leaflet.js (CDN) | Mapa interactivo de geolocalización en el informe |

---
<img width="1510" height="2585" alt="sentinel" src="https://github.com/user-attachments/assets/6e0ec154-147b-4c91-9a3f-8a6179f7f4c8" />


## Aviso legal

SENTINEL realiza **únicamente reconocimiento pasivo**. Consulta datos disponibles públicamente — APIs de geolocalización de IPs, bases de datos de abuso públicas, feeds de inteligencia de amenazas abiertos y rangos de IPs cloud documentados públicamente. No explota vulnerabilidades, no accede a sistemas restringidos ni modifica ningún dato.

Asegúrate siempre de tener autorización antes de analizar infraestructura que no te pertenece.

---

## Autora

Desarrollado como práctica académica de ciberseguridad en **Evolve Academy**.
Diseñado para demostrar inteligencia de amenazas a nivel de IP como capacidad OSINT profesional.

Parte de la **DOMINI Suite** junto a [DOMINUS](https://github.com/youruser/dominus).

---

*SENTINEL — sabe quién llama antes de abrir la puerta.*
