import json
import csv
import yaml
import os
from typing import Dict, Optional
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ConfiguracionResponse, HorarioDia


class ConfiguracionService:
    _instance = None
    _cache = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfiguracionService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"

    def load_configuracion(self) -> ConfiguracionResponse:
        if self._cache is not None:
            return self._cache

        # Try different file formats in order of preference
        for loader in [self._load_json, self._load_csv, self._load_yaml]:
            try:
                config = loader()
                if config:
                    self._cache = config
                    return config
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error loading configuration: {e}")
                continue

        # Return default configuration if no file found
        return self._get_default_configuration()

    def _load_json(self) -> Optional[ConfiguracionResponse]:
        file_path = self.data_dir / "configuracion_laboral.json"
        if not file_path.exists():
            raise FileNotFoundError()

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return self._parse_json_format(data)

    def _load_csv(self) -> Optional[ConfiguracionResponse]:
        file_path = self.data_dir / "configuracion_laboral.csv"
        if not file_path.exists():
            raise FileNotFoundError()

        dias_laborales = {}
        horarios_por_dia = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dia = row['dia']
                es_laboral = str(row['es_laboral']).lower() in ['true', '1', 'yes', 'si']

                dias_laborales[dia] = es_laboral

                if es_laboral and row.get('hora_inicio') and row.get('hora_fin'):
                    horarios_por_dia[dia] = HorarioDia(
                        hora_inicio=row['hora_inicio'],
                        hora_fin=row['hora_fin']
                    )
                else:
                    horarios_por_dia[dia] = None

        return ConfiguracionResponse(
            dias_laborales=dias_laborales,
            horarios_por_dia=horarios_por_dia
        )

    def _load_yaml(self) -> Optional[ConfiguracionResponse]:
        file_path = self.data_dir / "configuracion_laboral.yaml"
        if not file_path.exists():
            raise FileNotFoundError()

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return self._parse_json_format(data)

    def _parse_json_format(self, data: dict) -> ConfiguracionResponse:
        dias_config = data.get('dias_laborales', {})

        dias_laborales = {}
        horarios_por_dia = {}

        for dia, config in dias_config.items():
            if isinstance(config, dict):
                es_laboral = config.get('es_laboral', False)
                dias_laborales[dia] = es_laboral

                if es_laboral and 'hora_inicio' in config and 'hora_fin' in config:
                    horarios_por_dia[dia] = HorarioDia(
                        hora_inicio=config['hora_inicio'],
                        hora_fin=config['hora_fin']
                    )
                else:
                    horarios_por_dia[dia] = None
            else:
                # Simple boolean format
                dias_laborales[dia] = bool(config)
                horarios_por_dia[dia] = None

        return ConfiguracionResponse(
            dias_laborales=dias_laborales,
            horarios_por_dia=horarios_por_dia
        )

    def _get_default_configuration(self) -> ConfiguracionResponse:
        return ConfiguracionResponse(
            dias_laborales={
                "lunes": True,
                "martes": True,
                "miercoles": True,
                "jueves": True,
                "viernes": True,
                "sabado": False,
                "domingo": False
            },
            horarios_por_dia={
                "lunes": HorarioDia(hora_inicio="07:30", hora_fin="17:30"),
                "martes": HorarioDia(hora_inicio="07:30", hora_fin="17:30"),
                "miercoles": HorarioDia(hora_inicio="07:30", hora_fin="17:30"),
                "jueves": HorarioDia(hora_inicio="07:30", hora_fin="17:30"),
                "viernes": HorarioDia(hora_inicio="07:00", hora_fin="16:30"),
                "sabado": None,
                "domingo": None
            }
        )

    def clear_cache(self):
        self._cache = None


# Global instance
configuracion_service = ConfiguracionService()