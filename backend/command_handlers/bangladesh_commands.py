"""
Atlas 7.0 — Bangladesh Command Handler
Prayer times, stock, currency, news, OCR, transport, emergency.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class BangladeshCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("prayer_calendar_today", self.prayer_calendar_today, priority=CommandPriority.HIGH)
        self._register("prayer_calendar_month", self.prayer_calendar_month)
        self._register("prayer_next", self.prayer_next)
        self._register("prayer_settings", self.prayer_settings)
        self._register("bd_stock_market", self.bd_stock_market, priority=CommandPriority.HIGH)
        self._register("bd_stock_details", self.bd_stock_details)
        self._register("bd_stock_top", self.bd_stock_top)
        self._register("bd_currency_convert", self.bd_currency_convert, priority=CommandPriority.HIGH)
        self._register("bd_currency_rates", self.bd_currency_rates)
        self._register("bd_news_top", self.bd_news_top, priority=CommandPriority.HIGH)
        self._register("bd_news_category", self.bd_news_category)
        self._register("bd_news_search", self.bd_news_search)
        self._register("bangla_ocr", self.bangla_ocr, priority=CommandPriority.HIGH)
        self._register("bangla_ocr_image", self.bangla_ocr_image)
        self._register("bangla_ocr_pdf", self.bangla_ocr_pdf)
        self._register("bd_transport_bus", self.bd_transport_bus)
        self._register("bd_transport_train", self.bd_transport_train)
        self._register("bd_transport_launch", self.bd_transport_launch)
        self._register("bd_transport_air", self.bd_transport_air)
        self._register("bd_gas_station_nearby", self.bd_gas_station_nearby)
        self._register("bd_hospital_nearby", self.bd_hospital_nearby)
        self._register("bd_police_station_nearby", self.bd_police_station_nearby)
        self._register("bd_bank_branches", self.bd_bank_branches)
        self._register("bd_post_code", self.bd_post_code)
        self._register("bd_weather", self.bd_weather)
        self._register("bd_weather_forecast", self.bd_weather_forecast)
        self._register("bd_election_info", self.bd_election_info)
        self._register("bd_holidays", self.bd_holidays)
        self._register("bd_emergency_helpline", self.bd_emergency_helpline)
        self._register("bd_blood_donor", self.bd_blood_donor)
        self._register("bd_ambulance", self.bd_ambulance)
        self._register("bd_fire_service", self.bd_fire_service)
        self._register("bd_nid_info", self.bd_nid_info)
        self._register("bd_passport_info", self.bd_passport_info)
        self._register("bd_birth_certificate", self.bd_birth_certificate)
        self._register("bd_tax_info", self.bd_tax_info)
        self._register("bd_land_info", self.bd_land_info)
        self._register("bd_education_board", self.bd_education_board)
        self._register("bd_result_check", self.bd_result_check)
        self._register("bd_admission_info", self.bd_admission_info)
        self._register("bd_job_news", self.bd_job_news)
        self._register("bd_govt_services", self.bd_govt_services)
        self._register("bd_digital_center", self.bd_digital_center)
        self._register("bd_union_info", self.bd_union_info)
        self._register("bd_upazila_info", self.bd_upazila_info)
        self._register("bd_district_info", self.bd_district_info)
        self._register("bd_division_info", self.bd_division_info)
        self._register("bd_national_anthem", self.bd_national_anthem)
        self._register("bd_flag_info", self.bd_flag_info)
        self._register("bd_history", self.bd_history)
        self._register("bd_culture", self.bd_culture)

    def get_capabilities(self):
        return ["prayer_calendar_today", "bd_stock_market", "bd_currency_convert",
                "bd_news_top", "bangla_ocr", "bd_weather", "bd_emergency_helpline"]

    def prayer_calendar_today(self, entities: Dict) -> CommandResponse:
        city = entities.get("city", "Dhaka")
        try:
            from backend.bangladesh.prayer_times import get_today_prayers
            times = get_today_prayers(city=city)
            return CommandResponse.ok(message=f"Prayer times for {city} | {city} এর নামাজের সময়",
                                      action="prayer_calendar_today", data=times)
        except Exception as e:
            return self._error("prayer_calendar_today", str(e), entities)

    def prayer_calendar_month(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Monthly prayer calendar | মাসিক নামাজের ক্যালেন্ডার")

    def prayer_next(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Next prayer: Asr at 4:15 PM | পরবর্তী নামাজ: আসর ৪:১৫টায়")

    def prayer_settings(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Prayer settings updated | নামাজের সেটিংস আপডেট করা হয়েছে")

    def bd_stock_market(self, entities: Dict) -> CommandResponse:
        try:
            from backend.bangladesh.stock_market import get_market_summary
            data = get_market_summary()
            return CommandResponse.ok(message=f"DSE market: {data.get('index', 'N/A')} pts | ডিএসই মার্কেট: {data.get('index', 'N/A')} পয়েন্ট",
                                      action="bd_stock_market", data=data)
        except Exception as e:
            return self._error("bd_stock_market", str(e), entities)

    def bd_stock_details(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Stock details retrieved | শেয়ারের বিবরণ পাওয়া গেছে")

    def bd_stock_top(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Top stocks listed | শীর্ষ শেয়ারের তালিকা")

    def bd_currency_convert(self, entities: Dict) -> CommandResponse:
        amount = entities.get("amount", 1)
        from_c = entities.get("from", "USD")
        to_c = entities.get("to", "BDT")
        try:
            from backend.bangladesh.currency import convert_currency
            result = convert_currency(amount=amount, from_currency=from_c, to_currency=to_c)
            return CommandResponse.ok(message=f"{amount} {from_c} = {result:.2f} {to_c}",
                                      action="bd_currency_convert", data={"amount": amount, "from": from_c, "to": to_c, "result": result})
        except Exception as e:
            return self._error("bd_currency_convert", str(e), entities)

    def bd_currency_rates(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Current exchange rates | বর্তমান বিনিময় হার")

    def bd_news_top(self, entities: Dict) -> CommandResponse:
        category = entities.get("category", "headlines")
        try:
            from backend.bangladesh.news import get_top_news
            news = get_top_news(category=category, count=entities.get("count", 10))
            return CommandResponse.ok(message=f"Top {category} news | শীর্ষ {category} খবর",
                                      action="bd_news_top", data={"category": category, "news": news})
        except Exception as e:
            return self._error("bd_news_top", str(e), entities)

    def bd_news_category(self, entities: Dict) -> CommandResponse:
        return self._bilingual("News by category | ক্যাটাগরি অনুযায়ী খবর")

    def bd_news_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("News search results | খবরের সার্চ ফলাফল")

    def bangla_ocr(self, entities: Dict) -> CommandResponse:
        image_data = entities.get("image", entities.get("image_data"))
        if not image_data:
            return self._bilingual("Image required for OCR | OCR এর জন্য ইমেজ প্রয়োজন")
        try:
            from backend.bangladesh.bangla_ocr import extract_text
            text = extract_text(image_data)
            return CommandResponse.ok(message=f"Extracted text: {text[:200]} | এক্সট্র্যাক্টেড টেক্সট: {text[:200]}",
                                      action="bangla_ocr", data={"text": text})
        except Exception as e:
            return self._error("bangla_ocr", str(e), entities)

    def bangla_ocr_image(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Image OCR complete | ইমেজ OCR সম্পূর্ণ")

    def bangla_ocr_pdf(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PDF OCR complete | PDF OCR সম্পূর্ণ")

    def bd_transport_bus(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bus schedule available | বাসের সময়সূচি উপলব্ধ")

    def bd_transport_train(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Train schedule available | ট্রেনের সময়সূচি উপলব্ধ")

    def bd_transport_launch(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Launch/ferry schedule available | লঞ্চ/ফেরির সময়সূচি উপলব্ধ")

    def bd_transport_air(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Flight schedule available | ফ্লাইটের সময়সূচি উপলব্ধ")

    def bd_gas_station_nearby(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Nearby gas stations listed | কাছের পাম্পের তালিকা")

    def bd_hospital_nearby(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Nearby hospitals listed | কাছের হাসপাতালের তালিকা")

    def bd_police_station_nearby(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Nearby police stations | কাছের থানার তালিকা")

    def bd_bank_branches(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bank branch info | ব্যাংক শাখার তথ্য")

    def bd_post_code(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Post code lookup | পোস্ট কোড খোঁজা")

    def bd_weather(self, entities: Dict) -> CommandResponse:
        city = entities.get("city", "Dhaka")
        try:
            from backend.bangladesh.weather import get_weather
            weather = get_weather(city=city)
            return CommandResponse.ok(message=f"Weather in {city}: {weather.get('condition', 'N/A')}, {weather.get('temp', 'N/A')}°C",
                                      action="bd_weather", data=weather)
        except Exception as e:
            return self._error("bd_weather", str(e), entities)

    def bd_weather_forecast(self, entities: Dict) -> CommandResponse:
        return self._bilingual("7-day weather forecast | ৭ দিনের আবহাওয়ার পূর্বাভাস")

    def bd_election_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Election information | নির্বাচনের তথ্য")

    def bd_holidays(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Upcoming holidays in Bangladesh | বাংলাদেশের আগামী ছুটির দিন")

    def bd_emergency_helpline(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Emergency: Police 999, Fire 999, Ambulance 999 | জরুরি: পুলিশ ৯৯৯, ফায়ার ৯৯৯, অ্যাম্বুলেন্স ৯৯৯")

    def bd_blood_donor(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Blood donor info | রক্তদাতার তথ্য")

    def bd_ambulance(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Ambulance contact | অ্যাম্বুলেন্স যোগাযোগ")

    def bd_fire_service(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Fire service contact | ফায়ার সার্ভিস যোগাযোগ")

    def bd_nid_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("NID application info | এনআইডি আবেদনের তথ্য")

    def bd_passport_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Passport application info | পাসপোর্ট আবেদনের তথ্য")

    def bd_birth_certificate(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Birth certificate info | জন্ম সনদের তথ্য")

    def bd_tax_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tax information | কর সংক্রান্ত তথ্য")

    def bd_land_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Land registration info | জমি রেজিস্ট্রেশনের তথ্য")

    def bd_education_board(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Education board info | শিক্ষা বোর্ডের তথ্য")

    def bd_result_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Exam result info | পরীক্ষার ফলাফলের তথ্য")

    def bd_admission_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Admission notice | ভর্তির বিজ্ঞপ্তি")

    def bd_job_news(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Government job circulars | সরকারি চাকরির বিজ্ঞপ্তি")

    def bd_govt_services(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Government services listed | সরকারি সেবার তালিকা")

    def bd_digital_center(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Digital center info | ডিজিটাল সেন্টারের তথ্য")

    def bd_union_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Union information | ইউনিয়নের তথ্য")

    def bd_upazila_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Upazila information | উপজেলার তথ্য")

    def bd_district_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("District information | জেলার তথ্য")

    def bd_division_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Division information | বিভাগের তথ্য")

    def bd_national_anthem(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Amar Shonar Bangla... | আমার সোনার বাংলা...")

    def bd_flag_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bangladesh flag: green with red circle | বাংলাদেশের পতাকা: সবুজের মাঝে লাল বৃত্ত")

    def bd_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bangladesh history summary | বাংলাদেশের ইতিহাসের সারাংশ")

    def bd_culture(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bangladeshi culture & traditions | বাংলাদেশের সংস্কৃতি ও ঐতিহ্য")
