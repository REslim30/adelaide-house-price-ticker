from datetime import date

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