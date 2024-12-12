from sqlalchemy import Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

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

    @classmethod
    def from_flight_dict(self, flight_dict):
        assert isinstance(flight_dict, dict)

        instructions_id = None
        if isinstance(flight_dict["instructions"], dict):
            instructions_id = flight_dict["instructions"].get("id", None)

        return self(
            icao = flight_dict["icao"],
            session_id = flight_dict["session_id"],
            aircraft_id = flight_dict["aircraft_id"],
            flight_id = flight_dict["flight_id"],
            callsign = flight_dict["callsign"],
            altitude = flight_dict["altitude"],
            ground_speed = flight_dict["ground_speed"],
            track = flight_dict["track"],
            latitude = flight_dict["latitude"],
            longitude = flight_dict["longitude"],
            vertical_rate = flight_dict["vertical_rate"],
            squawk = flight_dict["squawk"],
            alert_squawk_change = flight_dict["alert_squawk_change"],
            emergency_code = flight_dict["emergency_code"],
            spi_ident = flight_dict["spi_ident"],
            on_ground = flight_dict["on_ground"],
            timestamp = flight_dict["last_datetime"],
            atc_instructions_id = instructions_id
        )

    @classmethod
    def from_other_flight_info(self, other_flight_info):
        assert isinstance(other_flight_info, FlightInformation)
        return self(
            icao = other_flight_info.icao,
            session_id = other_flight_info.session_id,
            aircraft_id = other_flight_info.aircraft_id,
            flight_id = other_flight_info.flight_id,
            callsign = other_flight_info.callsign,
            altitude = other_flight_info.altitude,
            ground_speed = other_flight_info.ground_speed,
            track = other_flight_info.track,
            latitude = other_flight_info.latitude,
            longitude = other_flight_info.longitude,
            vertical_rate = other_flight_info.vertical_rate,
            squawk = other_flight_info.squawk,
            alert_squawk_change = other_flight_info.alert_squawk_change,
            emergency_code = other_flight_info.emergency_code,
            spi_ident = other_flight_info.spi_ident,
            on_ground = other_flight_info.on_ground,
            timestamp = other_flight_info.timestamp,
            atc_instructions_id = other_flight_info.atc_instructions_id
        )

    def __eq__(self, other):
        if isinstance(other, FlightInformation):
            if self.icao != other.icao:
                return False
            if self.session_id != other.session_id:
                return False
            if self.aircraft_id != other.aircraft_id:
                return False
            if self.flight_id != other.flight_id:
                return False
            if self.callsign != other.callsign:
                return False
            if self.altitude != other.altitude:
                return False
            if self.ground_speed != other.ground_speed:
                return False
            if self.track != other.track:
                return False
            if self.latitude != other.latitude:
                return False
            if self.longitude != other.longitude:
                return False
            if self.vertical_rate != other.vertical_rate:
                return False
            if self.squawk != other.squawk:
                return False
            if self.alert_squawk_change != other.alert_squawk_change:
                return False
            if self.emergency_code != other.emergency_code:
                return False
            if self.spi_ident != other.spi_ident:
                return False
            if self.on_ground != other.on_ground:
                return False
            if self.atc_instructions_id != other.atc_instructions_id:
                return False
            return True
        return False

class InstructionsFromATC(Base):
    __tablename__ = "atc_instructions"
    id: Mapped[int] = mapped_column(primary_key=True)
    atc_user_id: Mapped[str] = mapped_column(Text)
    altitude: Mapped[int] = mapped_column(Integer, nullable=True)
    ground_speed: Mapped[int] = mapped_column(Integer, nullable=True)
    track: Mapped[int] = mapped_column(Integer, nullable=True)
    vertical_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    flight_info: Mapped[List["FlightInformation"]] = relationship(back_populates="atc_instructions")
    timestamp: Mapped[DateTime] = mapped_column(DateTime)

    def __init__(self, atc_user_id, altitude, ground_speed, track, vertical_rate):
        self.atc_user_id = atc_user_id
        self.altitude = altitude
        self.ground_speed = ground_speed
        self.track = track
        self.vertical_rate = vertical_rate
        self.timestamp = datetime.now()