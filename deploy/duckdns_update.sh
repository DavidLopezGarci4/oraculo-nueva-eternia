#!/bin/bash
# === DuckDNS IP Auto-Updater ===
# Dominio: oraculo-eternia.duckdns.org

DOMAIN="oraculo-eternia"
TOKEN="336856a6-0b32-4eeb-9dd3-614af573d782"

echo url="https://www.duckdns.org/update?domains=$DOMAIN&token=$TOKEN&ip=" | curl -k -o /home/opc/duckdns/duck.log -K -
