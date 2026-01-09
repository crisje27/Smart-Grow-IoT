"""
Servicio InfluxDB - SMART GROW
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from app.config import settings


class InfluxService:
    """Cliente para InfluxDB 2.x"""
    
    def __init__(self):
        self.client = InfluxDBClient(
            url=settings.INFLUX_URL,
            token=settings.INFLUX_TOKEN,
            org=settings.INFLUX_ORG
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = settings.INFLUX_BUCKET
        self.org = settings.INFLUX_ORG
    
    async def get_latest(self) -> Optional[Dict[str, Any]]:
        """Obtiene la última lectura de sensores"""
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -5m)
            |> filter(fn: (r) => r._measurement == "sensor_data")
            |> last()
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        tables = self.query_api.query(query, org=self.org)
        
        for table in tables:
            for record in table.records:
                return {
                    "timestamp": record.get_time(),
                    "temperature": record.values.get("temperature", 0),
                    "humidity": record.values.get("humidity", 0),
                    "soil_humidity": record.values.get("soil_humidity", 0),
                    "soil_temp": record.values.get("soil_temp", 0),
                    "light": record.values.get("light", 0),
                    "pressure": record.values.get("pressure", 0),
                    "rssi": record.values.get("rssi"),
                    "snr": record.values.get("snr")
                }
        
        return None
    
    async def get_history(self, hours: int = 24, aggregation: str = "10m") -> List[Dict]:
        """Obtiene histórico de lecturas"""
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "sensor_data")
            |> aggregateWindow(every: {aggregation}, fn: mean, createEmpty: false)
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        tables = self.query_api.query(query, org=self.org)
        results = []
        
        for table in tables:
            for record in table.records:
                results.append({
                    "timestamp": record.get_time().isoformat(),
                    "temperature": round(record.values.get("temperature", 0), 1),
                    "humidity": round(record.values.get("humidity", 0), 1),
                    "soil_humidity": round(record.values.get("soil_humidity", 0), 1),
                    "soil_temp": round(record.values.get("soil_temp", 0), 1),
                    "light": round(record.values.get("light", 0), 0),
                    "pressure": round(record.values.get("pressure", 0), 1)
                })
        
        return results
    
    async def get_stats(self, hours: int, fields: List[str]) -> List[Dict]:
        """Calcula estadísticas por campo"""
        stats = []
        
        for field in fields:
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r._measurement == "sensor_data")
                |> filter(fn: (r) => r._field == "{field}")
            '''
            
            # Min
            min_query = query + '|> min()'
            min_result = self.query_api.query(min_query, org=self.org)
            min_val = 0
            for table in min_result:
                for record in table.records:
                    min_val = record.get_value()
            
            # Max
            max_query = query + '|> max()'
            max_result = self.query_api.query(max_query, org=self.org)
            max_val = 0
            for table in max_result:
                for record in table.records:
                    max_val = record.get_value()
            
            # Mean
            mean_query = query + '|> mean()'
            mean_result = self.query_api.query(mean_query, org=self.org)
            mean_val = 0
            for table in mean_result:
                for record in table.records:
                    mean_val = record.get_value()
            
            # Count
            count_query = query + '|> count()'
            count_result = self.query_api.query(count_query, org=self.org)
            count_val = 0
            for table in count_result:
                for record in table.records:
                    count_val = record.get_value()
            
            stats.append({
                "field": field,
                "min": round(min_val, 2) if min_val else 0,
                "max": round(max_val, 2) if max_val else 0,
                "mean": round(mean_val, 2) if mean_val else 0,
                "count": count_val
            })
        
        return stats
    
    async def get_by_node(self, node_id: str, hours: int) -> List[Dict]:
        """Obtiene datos de un nodo específico"""
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "sensor_data")
            |> filter(fn: (r) => r.node_id == "{node_id}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        tables = self.query_api.query(query, org=self.org)
        results = []
        
        for table in tables:
            for record in table.records:
                results.append({
                    "timestamp": record.get_time().isoformat(),
                    "temperature": record.values.get("temperature", 0),
                    "humidity": record.values.get("humidity", 0),
                    "soil_humidity": record.values.get("soil_humidity", 0),
                    "soil_temp": record.values.get("soil_temp", 0),
                    "light": record.values.get("light", 0),
                    "pressure": record.values.get("pressure", 0)
                })
        
        return results
    
    def close(self):
        """Cierra la conexión"""
        self.client.close()
