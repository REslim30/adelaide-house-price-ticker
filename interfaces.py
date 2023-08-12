from abc import ABC, abstractmethod
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMTotalPropertyStock, SQMVacancyRate, SQMWeeklyRents


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

    @abstractmethod
    def post_sqm_total_property_stock(self, index: SQMTotalPropertyStock) -> None:
        pass

    @abstractmethod
    def post_sqm_vacancy_rate(self, index: SQMVacancyRate) -> None:
        pass

class Crawler(ABC):
    @abstractmethod
    def crawl_core_logic_daily_home_value(self) -> CoreLogicDailyHomeValue:
        pass

    @abstractmethod
    def crawl_sqm_weekly_rents(self) -> SQMWeeklyRents:
        pass

    @abstractmethod
    def crawl_prop_track_house_prices(self) -> PropTrackHousePrices:
        pass

    @abstractmethod
    def crawl_sqm_total_property_stock(self) -> SQMTotalPropertyStock:
        pass

    @abstractmethod
    def crawl_sqm_vacancy_rate(self) -> SQMVacancyRate:
        pass

class Repository(ABC):
    @abstractmethod
    def post_core_logic_daily_home_value(self, index: CoreLogicDailyHomeValue) -> None:
        pass

    @abstractmethod
    def post_sqm_weekly_rents(self, index: SQMWeeklyRents) -> None:
        pass

    @abstractmethod
    def post_prop_track_house_prices(self, index: PropTrackHousePrices) -> None:
        pass

    @abstractmethod
    def post_sqm_total_property_stock(self) -> SQMTotalPropertyStock:
        pass

    @abstractmethod
    def post_sqm_vacancy_rate(self) -> SQMVacancyRate:
        pass