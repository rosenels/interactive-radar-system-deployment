from typing import List
from sqlalchemy import Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
# from datetime import datetime

class Base(DeclarativeBase):
    pass

class Configuration(Base):
    __tablename__ = "configuration"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(Text, unique=True)
    value: Mapped[str] = mapped_column(Text)

    def __init__(self, key, value):
        self.key = str(key)
        self.value = str(value)

class FlightInformation(Base):
    __tablename__ = "flight_information"
    id: Mapped[int] = mapped_column(primary_key=True)
    icao: Mapped[str] = mapped_column(Text)
    session_id: Mapped[int] = mapped_column(Integer, nullable=True)
    aircraft_id: Mapped[int] = mapped_column(Integer, nullable=True)
    flight_id: Mapped[int] = mapped_column(Integer, nullable=True)
    callsign: Mapped[str] = mapped_column(Text, nullable=True)
    altitude: Mapped[int] = mapped_column(Integer, nullable=True)
    ground_speed: Mapped[int] = mapped_column(Integer, nullable=True)
    track: Mapped[int] = mapped_column(Integer, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    vertical_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    squawk: Mapped[int] = mapped_column(Integer, nullable=True)
    alert_squawk_change: Mapped[int] = mapped_column(Integer, nullable=True)
    emergency_code: Mapped[int] = mapped_column(Integer, nullable=True)
    spi_ident: Mapped[int] = mapped_column(Integer, nullable=True)
    on_ground: Mapped[int] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime)
    atc_instructions_id: Mapped[int] = mapped_column(ForeignKey("atc_instructions.id"), nullable=True)
    atc_instructions: Mapped["InstructionsFromATC"] = relationship(back_populates="flight_info")

    def __init__(self, icao, session_id, aircraft_id, flight_id, callsign, altitude, ground_speed, track, latitude, longitude, vertical_rate, squawk, alert_squawk_change, emergency_code, spi_ident, on_ground, timestamp, atc_instructions_id):
        self.icao = icao
        self.session_id = session_id
        self.aircraft_id = aircraft_id
        self.flight_id = flight_id
        self.callsign = callsign
        self.altitude = altitude
        self.ground_speed = ground_speed
        self.track = track
        self.latitude = latitude
        self.longitude = longitude
        self.vertical_rate = vertical_rate
        self.squawk = squawk
        self.alert_squawk_change = alert_squawk_change
        self.emergency_code = emergency_code
        self.spi_ident = spi_ident
        self.on_ground = on_ground
        self.timestamp = timestamp
        self.atc_instructions_id = atc_instructions_id

    def __eq__(self, other):
        if isinstance(other, FlightInformation):
            return self.icao == other.icao and self.timestamp == other.timestamp
        return False

class InstructionsFromATC(Base):
    __tablename__ = "atc_instructions"
    id: Mapped[int] = mapped_column(primary_key=True)
    altitude: Mapped[int] = mapped_column(Integer, nullable=True)
    ground_speed: Mapped[int] = mapped_column(Integer, nullable=True)
    track: Mapped[int] = mapped_column(Integer, nullable=True)
    vertical_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    flight_info: Mapped[List["FlightInformation"]] = relationship(back_populates="atc_instructions")

    def __init__(self, altitude, ground_speed, track, vertical_rate):
        self.altitude = altitude
        self.ground_speed = ground_speed
        self.track = track
        self.vertical_rate = vertical_rate