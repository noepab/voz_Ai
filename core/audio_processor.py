"""
Módulo para el procesamiento avanzado de audio.
Incluye filtrado, normalización y detección de voz activa (VAD).
"""
import numpy as np
from scipy import signal
import webrtcvad
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, List
import sounddevice as sd

logger = logging.getLogger(__name__)

@dataclass
class AudioConfig:
    """Configuración para el procesamiento de audio."""
    sample_rate: int = 16000
    chunk_size: int = 1024
    vad_aggressiveness: int = 3
    noise_reduction: bool = True
    auto_gain: bool = True
    silence_threshold: int = 100  # Umbral de silencio (0-32767)

class AudioProcessor:
    """Procesador de audio con filtrado, normalización y VAD."""
    
    def __init__(self, config: AudioConfig):
        """Inicializa el procesador de audio con la configuración dada."""
        self.config = config
        self.vad = webrtcvad.Vad(config.vad_aggressiveness)
        self._init_filters()
        
        # Historial para el filtro de ruido
        self.noise_profile = None
        self.noise_reduction_factor = 0.1
        
        # Estado para la normalización automática
        self.target_level = 0.1  # Nivel objetivo de amplitud (0.0 a 1.0)
        
        logger.info("Procesador de audio inicializado")
    
    def _init_filters(self):
        """Inicializa los filtros de audio."""
        # Filtro paso banda para voz humana (300-3400 Hz)
        nyquist = 0.5 * self.config.sample_rate
        low = 300 / nyquist
        high = 3400 / nyquist
        self.b, self.a = signal.butter(5, [low, high], 'bandpass')
        
        # Filtro de reducción de ruido (filtro de mediana)
        self.median_window = 5
        
        logger.debug("Filtros de audio inicializados")
    
    def process_chunk(self, audio_data: np.ndarray) -> Optional[np.ndarray]:
        """
        Procesa un chunk de audio con todas las mejoras.
        
        Args:
            audio_data: Array de numpy con los datos de audio (mono, 16-bit)
            
        Returns:
            Array de numpy con el audio procesado o None si se considera silencio
        """
        if audio_data.size == 0:
            return None
        
        # Aplicar filtro paso banda
        filtered = signal.filtfilt(self.b, self.a, audio_data.astype(np.float32))
        
        # Reducción de ruido (si está habilitada)
        if self.config.noise_reduction:
            filtered = self._reduce_noise(filtered)
        
        # Normalización automática (si está habilitada)
        if self.config.auto_gain:
            filtered = self._auto_gain(filtered)
        
        # Convertir a formato de 16 bits para VAD
        audio_int16 = (filtered * 32767).astype(np.int16)
        
        # Verificar si hay voz
        if self._is_speech(audio_int16):
            return audio_int16
        
        return None
    
    def _reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """Aplica reducción de ruido al audio."""
        # Actualizar perfil de ruido (primeros segundos se consideran ruido)
        if self.noise_profile is None:
            self.noise_profile = np.abs(audio)
        else:
            self.noise_profile = (1 - self.noise_reduction_factor) * self.noise_profile + \
                               self.noise_reduction_factor * np.abs(audio)
        
        # Aplicar reducción espectral
        noise_reduced = audio - self.noise_reduction_factor * self.noise_profile
        return np.clip(noise_reduced, -1.0, 1.0)
    
    def _auto_gain(self, audio: np.ndarray) -> np.ndarray:
        """Ajusta automáticamente la ganancia del audio."""
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            gain = self.target_level / max_amplitude
            return np.clip(audio * gain, -1.0, 1.0)
        return audio
    
    def _is_speech(self, audio_chunk: np.ndarray) -> bool:
        """Determina si el chunk de audio contiene voz."""
        try:
            # Verificar nivel de volumen
            if np.max(np.abs(audio_chunk)) < self.config.silence_threshold:
                return False
                
            # Usar VAD para detección de voz
            return self.vad.is_speech(
                audio_chunk.tobytes(),
                sample_rate=self.config.sample_rate
            )
        except Exception as e:
            logger.warning(f"Error en detección de voz: {e}")
            return False
    
    @staticmethod
    def list_audio_devices() -> List[dict]:
        """Lista los dispositivos de audio disponibles."""
        devices = []
        try:
            host_apis = sd.query_hostapis()
            for i, device in enumerate(sd.query_devices()):
                try:
                    devices.append({
                        'id': i,
                        'name': device['name'],
                        'hostapi': host_apis[device['hostapi']]['name'],
                        'max_input_channels': device['max_input_channels'],
                        'default_samplerate': device['default_samplerate']
                    })
                except Exception as e:
                    logger.warning(f"Error al obtener info del dispositivo {i}: {e}")
        except Exception as e:
            logger.error(f"Error al listar dispositivos de audio: {e}")
        
        return devices
    
    @staticmethod
    def find_input_device(device_name: str = None) -> Optional[int]:
        """Encuentra el ID del dispositivo de entrada por nombre."""
        devices = AudioProcessor.list_audio_devices()
        
        if not devices:
            return None
            
        if device_name is None:
            # Devolver el dispositivo predeterminado
            return sd.default.device[0]
            
        # Buscar dispositivo por nombre (insensible a mayúsculas)
        device_name = device_name.lower()
        for device in devices:
            if (device_name in device['name'].lower() and 
                device['max_input_channels'] > 0):
                return device['id']
                
        logger.warning(f"No se encontró el dispositivo: {device_name}")
        return None
