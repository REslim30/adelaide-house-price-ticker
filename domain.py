from datetime import date, datetime


class CoreLogicDailyHomeValue:
    def __init__(self, date: date, change_day_on_day: float, value: float) -> None:
        self.date = date
        self.change_day_on_day = change_day_on_day
        self.value = value
        pass


class SQMWeeklyRents:
    def __init__(self, week_ending_on_date: date, change_on_prev_week: float, dollar_value: float) -> None:
        self.week_ending_on_date = week_ending_on_date
        self.change_on_prev_week = change_on_prev_week
        self.dollar_value = dollar_value


class PropTrackHousePrices:
    def __init__(self, month_starting_on: date, monthly_growth_percentage: float, median_dollar_value: float) -> None:
        self.month_starting_on = month_starting_on
        self.monthly_growth_percentage = monthly_growth_percentage
        self.median_dollar_value = median_dollar_value
        pass


class SQMTotalPropertyStock:
    def __init__(self, month_starting_on: date, total_stock: int, month_on_month_change: int) -> None:
        self.month_starting_on = month_starting_on
        self.total_stock = total_stock
        self.month_on_month_change = month_on_month_change
        pass


class SQMVacancyRate:
    def __init__(self, month_starting_on: date, vacancy_rate: float, month_on_month_change: float) -> None:
        self.month_starting_on = month_starting_on
        # Rate of vacancy as a proportion
        self.vacancy_rate = vacancy_rate
        # Change in vacancy rate as a delta
        self.month_on_month_change = month_on_month_change
        pass


class QuarterlyMedianHouseSales:
    def __init__(self, year: int, quarter: int, download_link: str, excel_data: bytes) -> None:
        self.year = year
        # From 1 to 4
        self.quarter = quarter
        self.download_link = download_link
        # Excel spreadsheet
        self.excel_data = excel_data


class Quarter:
    def __init__(self, year: int, quarter: int) -> None:
        self.year = year
        # From 1 to 4
        self.quarter = quarter
        pass

    @staticmethod
    def from_date(date_obj: datetime or date) -> "Quarter":
        return Quarter(date_obj.year, Quarter.get_quarter(date_obj.month))

    def __eq__(self, other):
        return self.year == other.year and self.quarter == other.quarter

    @staticmethod
    def get_quarter(month: int) -> int:
        if month <= 3:
            return 1
        elif month <= 6:
            return 2
        elif month <= 9:
            return 3
        elif month <= 12:
            return 4
        else:
            raise Exception("Invalid month: " + str(month))

    def previous_quarter(self) -> "Quarter":
        if self.quarter == 1:
            return Quarter(self.year - 1, 4)
        else:
            return Quarter(self.year, self.quarter - 1)
