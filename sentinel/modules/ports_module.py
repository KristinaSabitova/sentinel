"""Port scanning via system nmap or masscan."""

from __future__ import annotations

import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from typing import Any

PORTS = "21,22,23,25,53,80,110,143,443,445,993,995,1433,1521,2049,2375,3306,3389,5432,5900,6379,8080,8443,9200,11211,27017"


class PortsModule:
    def __init__(self, timeout: int = 20, scanner: str = "auto") -> None:
        self.timeout = timeout
        self.scanner = scanner

    def run(self, ip: str) -> dict[str, Any]:
        resolved = self._resolve_scanner()
        if resolved is None:
            return {"ok": False, "skipped": True, "reason": "nmap y masscan no encontrados"}
        if resolved == "masscan":
            return self._run_masscan(ip)
        return self._run_nmap(ip)

    def _resolve_scanner(self) -> str | None:
        if self.scanner == "nmap":
            return "nmap" if shutil.which("nmap") else None
        if self.scanner == "masscan":
            return "masscan" if shutil.which("masscan") else None
        # auto: masscan preferido (menos ruidoso), nmap como fallback
        if shutil.which("masscan"):
            return "masscan"
        if shutil.which("nmap"):
            return "nmap"
        return None

    def _run_nmap(self, ip: str) -> dict[str, Any]:
        command = ["nmap", "-Pn", "-T3", "--open", "-p", PORTS, "-oX", "-", ip]
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=max(self.timeout * 3, 45),
        )
        if completed.returncode not in (0, 1):
            raise RuntimeError(completed.stderr.strip() or "nmap failed")
        return self._parse_xml(completed.stdout, command)

    def _run_masscan(self, ip: str) -> dict[str, Any]:
        command = ["masscan", f"-p{PORTS}", ip, "--rate=100", "-oX", "-"]
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=max(self.timeout * 3, 45),
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "masscan failed")
        return self._parse_xml(completed.stdout, command)

    def _parse_xml(self, xml_output: str, command: list[str]) -> dict[str, Any]:
        open_ports: list[dict[str, Any]] = []
        if xml_output.strip():
            # masscan emite un DOCTYPE vacío que puede confundir algunos parsers
            clean = re.sub(r"<!DOCTYPE[^>]*>", "", xml_output)
            root = ET.fromstring(clean)
            for port_node in root.findall(".//port"):
                state = port_node.find("state")
                if state is None or state.attrib.get("state") != "open":
                    continue
                service = port_node.find("service")
                port = int(port_node.attrib["portid"])
                name = service.attrib.get("name", "unknown") if service is not None else "unknown"
                product = service.attrib.get("product", "") if service is not None else ""
                open_ports.append(
                    {
                        "port": port,
                        "protocol": port_node.attrib.get("protocol", "tcp"),
                        "service": name,
                        "product": product,
                        "severity": self._severity(port),
                    }
                )
        return {"ok": True, "open_ports": open_ports, "count": len(open_ports), "command": " ".join(command)}

    def _severity(self, port: int) -> str:
        if port in {23, 445, 2375, 3389, 5900, 6379, 9200, 11211, 27017}:
            return "danger"
        if port in {21, 22, 25, 1433, 1521, 2049, 3306, 5432, 8080, 8443}:
            return "warning"
        return "safe"
