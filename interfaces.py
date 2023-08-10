from abc import ABC, abstractmethod
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMWeeklyRents


class MessagePoster(ABC):
    @abstractmethod
    def post_core_logic_daily_home_value(self, index: CoreLogicDailyHomeValue) -> None:
        pass
    
    @abstractmethod
    def post_sqm_weekly_rents(self, index: SQMWeeklyRents) -> None:
        pass

    @abstractmethod
    def post_prop_track_house_prices(self, index: PropTrackHousePrices) -> None:
        pass