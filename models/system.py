from sqlalchemy.orm import Mapped

from .base import *


class IPLocation(ModelBase):
    """
    IP地址归属地
    """
    __tablename__ = 'ip_location'
    id: Mapped[str_id] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(index=True, comment='IP版本，4或者6')
    start: Mapped[int] = mapped_column(index=True)
    end: Mapped[int] = mapped_column(index=True)
    country_code: Mapped[str_small]
    country: Mapped[str_medium]
    region: Mapped[str_medium]
    city: Mapped[str_medium]
    latitude: Mapped[float]
    longitude: Mapped[float]

    @classmethod
    def from_data(cls,
                  ip_version: int,
                  start_ip,
                  end_ip,
                  country_code,
                  country,
                  region,
                  city,
                  latitude,
                  longitude,
                  ):
        item = cls()
        item.version = ip_version
        item.start = int(start_ip)
        item.end = int(end_ip)
        item.country_code = country_code
        item.country = country
        item.region = region
        item.city = city
        item.latitude = float(latitude)
        item.longitude = float(longitude)
        return item
