"""Pydantic domain models."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class SermonInfo(BaseModel):
    title: str
    speaker: str
    scripture: Optional[str] = None
    series: Optional[str] = None
    notes: Optional[str] = None


class StreamConfig(BaseModel):
    title: str
    description: str = ""
    scheduled_for: Optional[datetime] = None
    destinations: list[str] = Field(default_factory=list)
    privacy: str = "public"


class ServiceEvent(BaseModel):
    name: str
    service_date: date
    start_time: Optional[datetime] = None
    stream: Optional[StreamConfig] = None
    sermon: Optional[SermonInfo] = None
