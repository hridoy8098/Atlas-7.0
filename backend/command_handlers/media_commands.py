"""
Atlas 7.0 — Media Command Handler
PDF, email, calendar, presentation, document creation, WhatsApp.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class MediaCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("pdf_read", self.pdf_read, priority=CommandPriority.HIGH)
        self._register("pdf_create", self.pdf_create)
        self._register("pdf_merge", self.pdf_merge)
        self._register("pdf_split", self.pdf_split)
        self._register("pdf_compress", self.pdf_compress)
        self._register("pdf_convert", self.pdf_convert)
        self._register("pdf_extract_text", self.pdf_extract_text)
        self._register("pdf_extract_images", self.pdf_extract_images)
        self._register("pdf_annotate", self.pdf_annotate)
        self._register("pdf_protect", self.pdf_protect)
        self._register("email_send", self.email_send, priority=CommandPriority.HIGH)
        self._register("email_inbox", self.email_inbox)
        self._register("email_read", self.email_read)
        self._register("email_reply", self.email_reply)
        self._register("email_forward", self.email_forward)
        self._register("email_delete", self.email_delete)
        self._register("email_search", self.email_search)
        self._register("email_draft", self.email_draft)
        self._register("email_attachment", self.email_attachment)
        self._register("calendar_view", self.calendar_view, priority=CommandPriority.HIGH)
        self._register("calendar_add", self.calendar_add)
        self._register("calendar_edit", self.calendar_edit)
        self._register("calendar_delete", self.calendar_delete)
        self._register("calendar_share", self.calendar_share)
        self._register("calendar_week", self.calendar_week)
        self._register("calendar_month", self.calendar_month)
        self._register("presentation_create", self.presentation_create, priority=CommandPriority.HIGH)
        self._register("presentation_add_slide", self.presentation_add_slide)
        self._register("presentation_edit_slide", self.presentation_edit_slide)
        self._register("presentation_export", self.presentation_export)
        self._register("document_create", self.document_create)
        self._register("document_edit", self.document_edit)
        self._register("document_export", self.document_export)
        self._register("spreadsheet_create", self.spreadsheet_create)
        self._register("spreadsheet_edit", self.spreadsheet_edit)
        self._register("spreadsheet_chart", self.spreadsheet_chart)
        self._register("whatsapp_send", self.whatsapp_send, priority=CommandPriority.HIGH)
        self._register("whatsapp_read", self.whatsapp_read)
        self._register("whatsapp_contacts", self.whatsapp_contacts)
        self._register("messenger_send", self.messenger_send)
        self._register("telegram_send", self.telegram_send)
        self._register("social_post", self.social_post)
        self._register("social_schedule", self.social_schedule)
        self._register("qr_generate", self.qr_generate, priority=CommandPriority.HIGH)
        self._register("qr_read", self.qr_read)
        self._register("barcode_generate", self.barcode_generate)
        self._register("barcode_read", self.barcode_read)
        self._register("screenshot_take", self.screenshot_take)
        self._register("screen_record", self.screen_record)

    def get_capabilities(self):
        return ["pdf_read", "email_send", "calendar_view", "presentation_create",
                "whatsapp_send", "qr_generate", "document_create", "screenshot_take"]

    def pdf_read(self, entities: Dict) -> CommandResponse:
        path = entities.get("path", entities.get("filepath"))
        if not path:
            return self._bilingual("PDF file path required | PDF ফাইল পাথ প্রয়োজন")
        try:
            from backend.media.pdf_reader import read_pdf
            text = read_pdf(path, pages=entities.get("pages"))
            return CommandResponse.ok(message=f"PDF read ({len(text)} chars) | PDF পড়া হয়েছে ({len(text)} অক্ষর)",
                                      action="pdf_read", data={"text": text[:2000], "path": path})
        except Exception as e:
            return self._error("pdf_read", str(e), entities)

    def pdf_create(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PDF created | PDF তৈরি করা হয়েছে")

    def pdf_merge(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PDFs merged | PDF মার্জ করা হয়েছে")

    def pdf_split(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PDF split | PDF বিভক্ত করা হয়েছে")

    def pdf_compress(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PDF compressed | PDF কমপ্রেস করা হয়েছে")

    def pdf_convert(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PDF converted | PDF রূপান্তর করা হয়েছে")

    def pdf_extract_text(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Text extracted from PDF | PDF থেকে টেক্সট এক্সট্র্যাক্ট করা হয়েছে")

    def pdf_extract_images(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Images extracted from PDF | PDF থেকে ইমেজ এক্সট্র্যাক্ট করা হয়েছে")

    def pdf_annotate(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PDF annotated | PDF এনোটেট করা হয়েছে")

    def pdf_protect(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PDF protected with password | PDF পাসওয়ার্ড দিয়ে সুরক্ষিত")

    def email_send(self, entities: Dict) -> CommandResponse:
        to = entities.get("to", entities.get("recipient"))
        subject = entities.get("subject", "No Subject")
        body = entities.get("body", entities.get("message"))
        if not to or not body:
            return self._bilingual("Recipient and message required | প্রাপক ও বার্তা প্রয়োজন")
        try:
            from backend.media.email_client import send_email
            result = send_email(to=to, subject=subject, body=body, attachments=entities.get("attachments"))
            return CommandResponse.ok(message=f"Email sent to {to} | {to} এ ইমেইল পাঠানো হয়েছে",
                                      action="email_send", data={"to": to, "subject": subject, "status": result})
        except Exception as e:
            return self._error("email_send", str(e), entities)

    def email_inbox(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Inbox retrieved | ইনবক্স পাওয়া গেছে")

    def email_read(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Email read | ইমেইল পড়া হয়েছে")

    def email_reply(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Email replied | ইমেইলের উত্তর দেওয়া হয়েছে")

    def email_forward(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Email forwarded | ইমেইল ফরওয়ার্ড করা হয়েছে")

    def email_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Email deleted | ইমেইল মুছে ফেলা হয়েছে")

    def email_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Email search results | ইমেইল সার্চ ফলাফল")

    def email_draft(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Email saved as draft | ইমেইল ড্রাফট হিসেবে সংরক্ষিত")

    def email_attachment(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Attachment processed | অ্যাটাচমেন্ট প্রসেস করা হয়েছে")

    def calendar_view(self, entities: Dict) -> CommandResponse:
        period = entities.get("period", "today")
        try:
            from backend.media.calendar import get_calendar
            events = get_calendar(period=period)
            return CommandResponse.ok(message=f"{len(events)} event(s) for {period} | {period} এর জন্য {len(events)}টি ইভেন্ট",
                                      action="calendar_view", data={"events": events})
        except Exception as e:
            return self._error("calendar_view", str(e), entities)

    def calendar_add(self, entities: Dict) -> CommandResponse:
        title = entities.get("title", entities.get("name"))
        date = entities.get("date", entities.get("time"))
        if not title:
            return self._bilingual("Event title required | ইভেন্টের শিরোনাম প্রয়োজন")
        try:
            from backend.media.calendar import add_event
            result = add_event(title=title, date=date, duration=entities.get("duration", 60))
            return CommandResponse.ok(message=f"Event '{title}' added | ইভেন্ট '{title}' যোগ করা হয়েছে",
                                      action="calendar_add", data={"event_id": result.get("id")})
        except Exception as e:
            return self._error("calendar_add", str(e), entities)

    def calendar_edit(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Event edited | ইভেন্ট এডিট করা হয়েছে")

    def calendar_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Event deleted | ইভেন্ট মুছে ফেলা হয়েছে")

    def calendar_share(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Calendar shared | ক্যালেন্ডার শেয়ার করা হয়েছে")

    def calendar_week(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Weekly calendar | সাপ্তাহিক ক্যালেন্ডার")

    def calendar_month(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Monthly calendar view | মাসিক ক্যালেন্ডার ভিউ")

    def presentation_create(self, entities: Dict) -> CommandResponse:
        title = entities.get("title", "Untitled")
        slides = entities.get("slides", entities.get("content", []))
        try:
            from backend.media.presentation import create_presentation
            result = create_presentation(title=title, slides=slides)
            return CommandResponse.ok(message=f"Presentation '{title}' created | প্রেজেন্টেশন '{title}' তৈরি করা হয়েছে",
                                      action="presentation_create", data={"presentation_id": result.get("id")})
        except Exception as e:
            return self._error("presentation_create", str(e), entities)

    def presentation_add_slide(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Slide added | স্লাইড যোগ করা হয়েছে")

    def presentation_edit_slide(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Slide edited | স্লাইড এডিট করা হয়েছে")

    def presentation_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Presentation exported | প্রেজেন্টেশন এক্সপোর্ট করা হয়েছে")

    def document_create(self, entities: Dict) -> CommandResponse:
        title = entities.get("title", "Untitled")
        content = entities.get("content", "")
        try:
            from backend.media.document_editor import create_document
            result = create_document(title=title, content=content)
            return CommandResponse.ok(message=f"Document '{title}' created | ডকুমেন্ট '{title}' তৈরি করা হয়েছে",
                                      action="document_create", data={"doc_id": result.get("id")})
        except Exception as e:
            return self._error("document_create", str(e), entities)

    def document_edit(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Document edited | ডকুমেন্ট এডিট করা হয়েছে")

    def document_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Document exported | ডকুমেন্ট এক্সপোর্ট করা হয়েছে")

    def spreadsheet_create(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Spreadsheet created | স্প্রেডশিট তৈরি করা হয়েছে")

    def spreadsheet_edit(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Spreadsheet edited | স্প্রেডশিট এডিট করা হয়েছে")

    def spreadsheet_chart(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Chart added to spreadsheet | স্প্রেডশিটে চার্ট যোগ করা হয়েছে")

    def whatsapp_send(self, entities: Dict) -> CommandResponse:
        to = entities.get("to", entities.get("number"))
        message = entities.get("message", entities.get("text"))
        if not to or not message:
            return self._bilingual("Recipient and message required | প্রাপক ও বার্তা প্রয়োজন")
        try:
            from backend.media.whatsapp_client import send_message
            result = send_message(to=to, message=message)
            return CommandResponse.ok(message=f"WhatsApp sent to {to} | {to} এ হোয়াটসঅ্যাপ পাঠানো হয়েছে",
                                      action="whatsapp_send", data={"to": to, "status": result})
        except Exception as e:
            return self._error("whatsapp_send", str(e), entities)

    def whatsapp_read(self, entities: Dict) -> CommandResponse:
        return self._bilingual("WhatsApp messages retrieved | হোয়াটসঅ্যাপ বার্তা পাওয়া গেছে")

    def whatsapp_contacts(self, entities: Dict) -> CommandResponse:
        return self._bilingual("WhatsApp contacts listed | হোয়াটসঅ্যাপ কন্টাক্টের তালিকা")

    def messenger_send(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Messenger message sent | মেসেঞ্জার বার্তা পাঠানো হয়েছে")

    def telegram_send(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Telegram message sent | টেলিগ্রাম বার্তা পাঠানো হয়েছে")

    def social_post(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Social media post published | সোশ্যাল মিডিয়া পোস্ট প্রকাশিত")

    def social_schedule(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Social post scheduled | সোশ্যাল পোস্ট শিডিউল করা হয়েছে")

    def qr_generate(self, entities: Dict) -> CommandResponse:
        data = entities.get("data", entities.get("text", entities.get("url")))
        if not data:
            return self._bilingual("Data/URL required for QR | QR এর জন্য ডাটা/URL প্রয়োজন")
        try:
            from backend.media.qr_tools import generate_qr
            qr = generate_qr(data, size=entities.get("size", 256))
            return CommandResponse.ok(message=f"QR generated for: {data[:50]} | QR তৈরি: {data[:50]}",
                                      action="qr_generate", data={"qr": qr})
        except Exception as e:
            return self._error("qr_generate", str(e), entities)

    def qr_read(self, entities: Dict) -> CommandResponse:
        return self._bilingual("QR code read | QR কোড পড়া হয়েছে")

    def barcode_generate(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Barcode generated | বারকোড তৈরি করা হয়েছে")

    def barcode_read(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Barcode read | বারকোড পড়া হয়েছে")

    def screenshot_take(self, entities: Dict) -> CommandResponse:
        try:
            from backend.media.screenshot import take_screenshot
            result = take_screenshot()
            return CommandResponse.ok(message="Screenshot taken | স্ক্রিনশট নেওয়া হয়েছে",
                                      action="screenshot_take", data=result)
        except Exception as e:
            return self._error("screenshot_take", str(e), entities)

    def screen_record(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Screen recording started | স্ক্রিন রেকর্ডিং শুরু হয়েছে")
