# Copyright 2017-19 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2021 Moka Tourisme (https://www.mokatourisme.fr).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class EventSession(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mail_template_reminder = cls.env.ref("event_session.event_session_reminder")
        cls.mail_template_badge = cls.env.ref(
            "event_session.event_session_registration_mail_template_badge"
        )
        cls.event = cls.env["event.event"].create(
            {
                "name": "Test event",
                "use_sessions": True,
                "seats_limited": True,
                "seats_max": "5",
                "event_mail_ids": [
                    (0, 0, vals)
                    for vals in [
                        {
                            "interval_nbr": 15,
                            "interval_unit": "days",
                            "interval_type": "before_event",
                            "template_ref": f"mail.template,{cls.mail_template_reminder.id}",
                        },
                        {
                            "interval_nbr": 0,
                            "interval_unit": "hours",
                            "interval_type": "after_sub",
                            "template_ref": f"mail.template,{cls.mail_template_badge.id}",
                        },
                    ]
                ],
            }
        )
        cls.session = cls.env["event.session"].create(
            {
                "date_begin": "2017-05-26 20:00:00",
                "date_end": "2017-05-26 21:00:00",
                "event_id": cls.event.id,
            }
        )
        cls.timeslot_16_00 = cls.env.ref("event_session.timeslot_16_00")
        cls.timeslot_20_00 = cls.env.ref("event_session.timeslot_20_00")

    def test_session_name_get(self):
        # Case 1: Same tz than user
        name = self.session.name_get()[0][1]
        self.assertEqual(name, "Test event, May 26, 2017, 10:00:00 PM")
        # Case 2: Different timezone
        self.event.date_tz = "UTC"
        name = self.session.name_get()[0][1]
        self.assertEqual(name, "Test event, May 26, 2017, 8:00:00 PM (UTC)")

    def test_check_dates(self):
        with self.assertRaisesRegex(
            ValidationError,
            "The closing date cannot be earlier than the beginning date",
        ):
            self.session.date_end = "2017-05-26 19:00:00"

    def test_open_registrations(self):
        domain = self.session.action_open_registrations()["domain"]
        attendees = self.env["event.registration"].search(domain)
        self.assertEqual(attendees, self.session.registration_ids)

    def test_event_mail_sync_from_event(self):
        self.assertEqual(len(self.session.event_mail_ids), 2)
        # Case 1: Remove from event, removes from sessions
        self.event.event_mail_ids[0].unlink()
        self.assertEqual(len(self.session.event_mail_ids), 1)
        # Case 2: Add a new template
        event_mail = self.env["event.mail"].create(
            {
                "event_id": self.event.id,
                "interval_nbr": 5,
                "interval_unit": "days",
                "interval_type": "before_event",
                "template_ref": f"mail.template,{self.mail_template_reminder.id}",
            }
        )
        session_mail = self.session.event_mail_ids.filtered(
            lambda r: r.scheduler_id == event_mail
        )
        self.assertTrue(session_mail)
        self.assertEqual(event_mail.interval_nbr, session_mail.interval_nbr)
        self.assertEqual(event_mail.interval_unit, session_mail.interval_unit)
        self.assertEqual(event_mail.interval_type, session_mail.interval_type)
        self.assertEqual(event_mail.template_ref, session_mail.template_ref)

    def test_event_mail_compute_scheduled_date(self):
        event_mail = self.event.event_mail_ids.filtered(
            lambda m: m.interval_type == "before_event"
        )
        session_mail = self.session.event_mail_ids.filtered(
            lambda m: m.scheduler_id == event_mail
        )
        # Case 1: 15 days before event
        event_mail.interval_nbr = 10
        expected = self.session.date_begin - timedelta(days=10)
        self.assertEqual(session_mail.scheduled_date, expected)
        self.assertFalse(event_mail.scheduled_date)
        # Case 2: 2 days after event
        event_mail.interval_nbr = 2
        event_mail.interval_type = "after_event"
        expected = self.session.date_end + timedelta(days=2)
        self.assertEqual(session_mail.scheduled_date, expected)
        self.assertFalse(event_mail.scheduled_date)
        # Case 3: after sub
        event_mail.interval_nbr = 0
        event_mail.interval_type = "after_sub"
        self.assertEqual(session_mail.scheduled_date, self.session.create_date)
        self.assertFalse(event_mail.scheduled_date)

    def test_event_mail_registration_compute_scheduled_date(self):
        session_mail = self.session.event_mail_ids.filtered(
            lambda m: m.interval_type == "after_sub"
        )
        self.env["event.registration"].create(
            {
                "name": "Test Attendee",
                "event_id": self.event.id,
                "session_id": self.session.id,
                "state": "open",
            }
        )
        mail_registration = session_mail._create_missing_mail_registrations(
            session_mail._get_new_event_registrations()
        )
        expected = mail_registration.registration_id.date_open
        self.assertEqual(mail_registration.scheduled_date, expected)

    def test_session_seats(self):
        self.assertEqual(self.event.seats_unconfirmed, self.session.seats_unconfirmed)
        self.assertEqual(self.event.seats_used, self.session.seats_used)
        vals = {
            "name": "Test Attendee",
            "event_id": self.event.id,
            "session_id": self.session.id,
            "state": "open",
        }
        # Fill the event session with attendees
        self.env["event.registration"].create([vals] * self.session.seats_available)
        # Try to create another one
        msg = "No more available seats."
        with self.assertRaisesRegex(ValidationError, msg):
            registration = self.env["event.registration"].create(vals)
        # Temporarily allow to create a draft registration and attempt to confirm it
        self.event.seats_limited = False
        registration = self.env["event.registration"].create(dict(vals, state="draft"))
        self.event.seats_limited = True
        msg = "No more available seats."
        with self.assertRaisesRegex(ValidationError, msg):
            registration.action_confirm()
            registration.flush()

    def test_session_seats_count(self):
        session_1, session_2 = self.env["event.session"].create(
            [
                {
                    "event_id": self.event.id,
                    "date_begin": fields.Datetime.now(),
                    "date_end": fields.Datetime.now() + timedelta(hours=1),
                },
                {
                    "event_id": self.event.id,
                    "date_begin": fields.Datetime.now() + timedelta(days=1),
                    "date_end": fields.Datetime.now() + timedelta(days=1, hours=1),
                },
            ]
        )
        attendee_1, attendee_2, attendee_3 = self.env["event.registration"].create(
            [
                {
                    "name": "S1: First Atendee",
                    "event_id": self.event.id,
                    "session_id": session_1.id,
                },
                {
                    "name": "S1: Second Atendee",
                    "event_id": self.event.id,
                    "session_id": session_1.id,
                },
                {
                    "name": "S2: First Atendee",
                    "event_id": self.event.id,
                    "session_id": session_2.id,
                },
            ]
        )
        self.assertEqual(session_1.seats_unconfirmed, 2)
        self.assertEqual(session_2.seats_unconfirmed, 1)
        self.assertEqual(self.event.seats_unconfirmed, 3)
        self.assertEqual(session_1.seats_reserved, 0)
        self.assertEqual(session_2.seats_reserved, 0)
        self.assertEqual(self.event.seats_reserved, 0)
        attendee_1.action_confirm()
        self.assertEqual(session_1.seats_unconfirmed, 1)
        self.assertEqual(session_2.seats_unconfirmed, 1)
        self.assertEqual(self.event.seats_unconfirmed, 2)
        self.assertEqual(session_1.seats_reserved, 1)
        self.assertEqual(session_2.seats_reserved, 0)
        self.assertEqual(self.event.seats_reserved, 1)
        attendee_2.action_confirm()
        self.assertEqual(session_1.seats_unconfirmed, 0)
        self.assertEqual(session_2.seats_unconfirmed, 1)
        self.assertEqual(self.event.seats_unconfirmed, 1)
        self.assertEqual(session_1.seats_reserved, 2)
        self.assertEqual(session_2.seats_reserved, 0)
        self.assertEqual(self.event.seats_reserved, 2)
        attendee_3.action_confirm()
        self.assertEqual(session_1.seats_unconfirmed, 0)
        self.assertEqual(session_2.seats_unconfirmed, 0)
        self.assertEqual(self.event.seats_unconfirmed, 0)
        self.assertEqual(session_1.seats_reserved, 2)
        self.assertEqual(session_2.seats_reserved, 1)
        self.assertEqual(self.event.seats_reserved, 3)

    def assertSessionDates(self, sessions, expected):
        for session, date in zip(sessions, expected):
            local_date = fields.Datetime.context_timestamp(
                session._set_tz_context(), session.date_begin
            )
            local_date_str = fields.Datetime.to_string(local_date)
            self.assertEqual(local_date_str, date)

    def _wizard_generate_sessions(self, vals):
        wizard = self.env["wizard.event.session"].create(vals)
        sessions_domain = wizard.action_create_sessions()["domain"]
        return self.env["event.session"].search(sessions_domain)

    def test_session_create_wizard_weekly_01(self):
        # Mondays at 16:00 and 20:00, for whole Jan 2022
        # ╔════════════════════╗
        # ║ January ░░░░░ 2022 ║
        # ╟──┬──┬──┬──┬──┬──┬──╢
        # ║░░│░░│░░│░░│░░│░░│  ║
        # ╟──╔══╗──┼──┼──┼──┼──╢
        # ║  ║03║  │  │  │  │  ║
        # ╟──╠══╣──┼──┼──┼──┼──╢
        # ║  ║10║  │  │  │  │  ║
        # ╟──╠══╣──┼──┼──┼──┼──╢
        # ║  ║17║  │  │  │  │  ║
        # ╟──╠══╣──┼──┼──┼──┼──╢
        # ║  ║24║  │  │  │  │  ║
        # ╟──╠══╣──┼──┼──┼──┼──╢
        # ║  ║31║░░│░░│░░│░░│░░║
        # ╚══╚══╝══╧══╧══╧══╧══╝
        expected = [
            "2022-01-03 16:00:00",
            "2022-01-03 20:00:00",
            "2022-01-10 16:00:00",
            "2022-01-10 20:00:00",
            "2022-01-17 16:00:00",
            "2022-01-17 20:00:00",
            "2022-01-24 16:00:00",
            "2022-01-24 20:00:00",
            "2022-01-31 16:00:00",
            "2022-01-31 20:00:00",
        ]
        sessions = self._wizard_generate_sessions(
            {
                "event_id": self.event.id,
                "rrule_type": "weekly",
                "mon": True,
                "tue": False,
                "wed": False,
                "thu": False,
                "fri": False,
                "sun": False,
                "sat": False,
                "timeslot_ids": [
                    (6, 0, (self.timeslot_16_00 | self.timeslot_20_00).ids)
                ],
                "duration": 1.0,
                "start": "2022-01-01",
                "until": "2022-01-31",
            }
        )
        self.assertSessionDates(sessions, expected)

    def test_session_create_wizard_weekly_02(self):
        # Mondays, Wednesdays and Fridays at 20:00, every 2 weeks for a Feb 2022
        # ╔════════════════════╗
        # ║ February ░░░░ 2022 ║
        # ╟──┬──┬──╔══╗──╔══╗──╢
        # ║░░│░░│  ║02║  ║04║  ║
        # ╟──┼──┼──╚══╝──╚══╝──╢
        # ║  │  │  │  │  │  │  ║
        # ╟──╔══╗──╔══╗──╔══╗──╢
        # ║  ║14║  ║16║  ║18║  ║
        # ╟──╚══╝──╚══╝──╚══╝──╢
        # ║  │  │  │  │  │  │  ║
        # ╟──╔══╗──┼──┼──┼──┼──╢
        # ║  ║28║░░│░░│░░│░░│░░║
        # ╚══╚══╝══╧══╧══╧══╧══╝
        expected = [
            "2022-02-02 20:00:00",
            "2022-02-04 20:00:00",
            "2022-02-14 20:00:00",
            "2022-02-16 20:00:00",
            "2022-02-18 20:00:00",
            "2022-02-28 20:00:00",
        ]
        sessions = self._wizard_generate_sessions(
            {
                "event_id": self.event.id,
                "rrule_type": "weekly",
                "interval": 2,
                "mon": True,
                "tue": False,
                "wed": True,
                "thu": False,
                "fri": True,
                "sun": False,
                "sat": False,
                "timeslot_ids": [(6, 0, self.timeslot_20_00.ids)],
                "duration": 2.0,
                "start": "2022-02-01",
                "until": "2022-02-28",
            }
        )
        self.assertSessionDates(sessions, expected)

    def test_session_create_wizard_monthly(self):
        # Last sunday of each month at 16:00, from March 2022 to May 2022
        expected = [
            "2022-03-27 16:00:00",
            "2022-04-24 16:00:00",
            "2022-05-29 16:00:00",
        ]
        sessions = self._wizard_generate_sessions(
            {
                "event_id": self.event.id,
                "rrule_type": "monthly",
                "month_by": "day",
                "byday": "-1",
                "weekday": "SUN",
                "timeslot_ids": [(6, 0, self.timeslot_16_00.ids)],
                "duration": 1.0,
                "start": "2022-03-01",
                "until": "2022-05-31",
            }
        )
        self.assertSessionDates(sessions, expected)
