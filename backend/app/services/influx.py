"""
SMART GROW - Servicio InfluxDB
==============================
Cliente para interactuar con InfluxDB 2.x
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class InfluxService:
    """Servicio para interactuar con InfluxDB."""
    
    def __init__(self):
        """Inicializa la conexión con InfluxDB."""
        self.url = os.getenv('INFLUX_URL', 'http://localhost:8086')
        self.token = os.getenv('INFLUX_TOKEN', 'smartgrow-secret-token')
        self.org = os.getenv('INFLUX_ORG', 'smartgrow')
        self.bucket = os.getenv('INFLUX_BUCKET', 'agricola')
        
        self.client = InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org
        )
        
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        
        logger.info(f"InfluxDB conectado: {self.url}")
    
    def write_sensor_data(self, data: Dict[str, Any], node_id: str = "node1"):
        """
        Escribe datos de sensores a InfluxDB.
        
        Args:
            data: Diccionario con datos de sensores
            node_id: Identificador del nodo
        """
        point = Point("sensor_data") \
            .tag("node", node_id) \
            .field("temperature", float(data.get('temperature', 0))) \
            .field("humidity", float(data.get('humidity', 0))) \
            .field("soil_humidity", float(data.get('soil_humidity', 0))) \
            .field("soil_temp", float(data.get('soil_temp', 0))) \
            .field("light", float(data.get('light', 0))) \
            .field("pressure", float(data.get('pressure', 0))) \
            .field("rssi", int(data.get('rssi', 0))) \
            .field("snr", float(data.get('snr', 0)))
        
        self.write_api.write(bucket=self.bucket, record=point)
        logger.debug(f"Datos escritos para {node_id}")
    
    def query(self, flux_query: str) -> List[Dict]:
        """
        Ejecuta una consulta Flux.
        
        Args:
            flux_query: Consulta en lenguaje Flux
            
        Returns:
            Lista de resultados
        """
        tables = self.query_api.query(flux_query, org=self.org)
        
        results = []
        for table in tables:
            for record in table.records:
                results.append(record.values)
        
        return results
    
    def get_latest(self, node_id: str = "node1") -> Optional[Dict]:
        """
        Obtiene la última lectura de un nodo.
        
        Args:
            node_id: Identificador del nodo
            
        Returns:
            Última lectura o None
        """
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -1h)
            |> filter(fn: (r) => r._measurement == "sensor_data")
            |> filter(fn: (r) => r.node == "{node_id}")
            |> last()
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        results = self.query(query)
        return results[0] if results else None
    
    def get_history(
        self,
        hours: int = 24,
        interval: str = "10m",
        node_id: str = "node1"
    ) -> List[Dict]:
        """
        Obtiene histórico de datos agregados.
        
        Args:
            hours: Horas hacia atrás
            interval: Intervalo de agregación
            node_id: Identificador del nodo
            
        Returns:
            Lista de lecturas agregadas
        """
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "sensor_data")
            |> filter(fn: (r) => r.node == "{node_id}")
            |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        return self.query(query)
    
    def get_stats(
        self,
        hours: int = 24,
        field: str = "temperature",
        node_id: str = "node1"
    ) -> Dict:
        """
        Obtiene estadísticas de un campo.
        
        Args:
            hours: Período de cálculo
            field: Campo a analizar
            node_id: Identificador del nodo
            
        Returns:
            Estadísticas (min, max, mean, count)
        """
        query = f'''
            data = from(bucket: "{self.bucket}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "sensor_data")
            |> filter(fn: (r) => r.node == "{node_id}")
            |> filter(fn: (r) => r._field == "{field}")
            
            min = data |> min() |> yield(name: "min")
            max = data |> max() |> yield(name: "max")
            mean = data |> mean() |> yield(name: "mean")
            count = data |> count() |> yield(name: "count")
        '''
        
        results = self.query(query)
        
        stats = {"field": field, "min": 0, "max": 0, "mean": 0, "count": 0}
        for r in results:
            if "_value" in r:
                result_name = r.get("result", "")
                stats[result_name] = r["_value"]
        
        return stats
    
    def close(self):
        """Cierra la conexión con InfluxDB."""
        self.client.close()
        logger.info("Conexión InfluxDB cerrada")
