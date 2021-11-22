# Copyright 2017-19 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2021 Moka Tourisme (https://www.mokatourisme.fr).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
from odoo.tools import mute_logger

from .common import CommonEventSessionCase


class TestEventSession(CommonEventSessionCase):
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

    def test_event_event_sync_from_event_type(self):
        """Test that the event.type fields are synced to the event.event"""
        event_type = self.env["event.type"].create(
            {
                "name": "Test event type",
                "use_sessions": True,
            }
        )
        event = self.env["event.event"].create(
            {
                "name": "Test event",
                "event_type_id": event_type.id,
                "date_begin": self.event.date_begin,
                "date_end": self.event.date_end,
            }
        )
        self.assertEqual(event.use_sessions, True)

    def test_event_event_form(self):
        """Test UX on the event.event form"""
        event_form = Form(self.env["event.event"])
        event_form.name = "Test event sessions"
        # Case 1: Changing to a session event will fill dates automatically
        self.assertFalse(event_form.use_sessions)
        self.assertFalse(event_form.date_begin)
        event_form.use_sessions = True
        self.assertTrue(event_form.date_begin)
        self.assertTrue(event_form.date_end)

    def test_event_event_use_sessions_switch(self):
        # Case 1: We can't change an event to use_sessions after registrations
        event = self.env["event.event"].create(
            {
                "name": "Test event",
                "date_begin": self.event.date_begin,
                "date_end": self.event.date_end,
            }
        )
        self.env["event.registration"].create(
            {
                "event_id": event.id,
                "name": "Test attendee",
            }
        )
        msg = "You can't enable/disable sessions on events with registrations."
        with self.assertRaisesRegex(ValidationError, msg):
            event.use_sessions = True
        # Case 2: We can change it back, if we have no registrations
        # In fact event.sessions are removed when doing so
        self.event.use_sessions = False
        self.assertFalse(self.session.exists())

    @mute_logger("odoo.models.unlink")
    def test_event_event_sessions_count(self):
        """Test that the sessions count is computed correctly"""
        self.assertEqual(self.event.session_count, 1)
        self.session.unlink()
        self.assertEqual(self.event.session_count, 0)

    @mute_logger("odoo.models.unlink")
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
        """Test event session seats constraints"""
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

    def test_event_seats(self):
        """Test that event.event seats constraints do not apply to sessions"""
        # Case: Event has a limit of 5 seats, but it should apply per-session
        self.event.seats_max = 5
        self.event.seats_limited = True
        # Fill session with attendees
        vals = {
            "name": "Test Attendee",
            "event_id": self.event.id,
            "session_id": self.session.id,
            "state": "open",
        }
        self.env["event.registration"].create([vals] * self.session.seats_available)
        # Create a second session and fill it too
        session2 = self.session.copy({})
        vals["session_id"] = session2.id
        self.env["event.registration"].create([vals] * session2.seats_available)
        # Call explicitly just in case, this shouldn't raise anything
        self.event._check_seats_limit()

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
        self.assertEqual(session_1.seats_reserved, 0)
        self.assertEqual(session_1.seats_expected, 2)
        self.assertEqual(session_2.seats_unconfirmed, 1)
        self.assertEqual(session_2.seats_reserved, 0)
        self.assertEqual(session_2.seats_expected, 1)
        self.assertEqual(self.event.seats_unconfirmed, 3)
        self.assertEqual(self.event.seats_reserved, 0)
        self.assertEqual(self.event.seats_expected, 3)
        attendee_1.action_confirm()
        self.assertEqual(session_1.seats_unconfirmed, 1)
        self.assertEqual(session_1.seats_reserved, 1)
        self.assertEqual(session_2.seats_unconfirmed, 1)
        self.assertEqual(session_2.seats_reserved, 0)
        self.assertEqual(self.event.seats_unconfirmed, 2)
        self.assertEqual(self.event.seats_reserved, 1)
        attendee_2.action_confirm()
        self.assertEqual(session_1.seats_unconfirmed, 0)
        self.assertEqual(session_1.seats_reserved, 2)
        self.assertEqual(session_2.seats_unconfirmed, 1)
        self.assertEqual(session_2.seats_reserved, 0)
        self.assertEqual(self.event.seats_unconfirmed, 1)
        self.assertEqual(self.event.seats_reserved, 2)
        attendee_3.action_confirm()
        self.assertEqual(session_1.seats_unconfirmed, 0)
        self.assertEqual(session_1.seats_reserved, 2)
        self.assertEqual(session_2.seats_unconfirmed, 0)
        self.assertEqual(session_2.seats_reserved, 1)
        self.assertEqual(self.event.seats_unconfirmed, 0)
        self.assertEqual(self.event.seats_reserved, 3)

    def test_event_session_is_ongoing(self):
        # Case 1: Session is ongoing
        session = self.env["event.session"].create(
            {
                "event_id": self.event.id,
                "date_begin": fields.Datetime.now() - timedelta(hours=1),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
            }
        )
        ongoing = self.env["event.session"].search([("is_ongoing", "=", True)])
        not_ongoing = self.env["event.session"].search([("is_ongoing", "=", False)])
        self.assertTrue(session.is_ongoing)
        self.assertIn(session, ongoing)
        self.assertNotIn(session, not_ongoing)
        # Case 2: It isn't
        session.write(
            {
                "date_begin": fields.Datetime.now() + timedelta(days=1),
                "date_end": fields.Datetime.now() + timedelta(days=1, hours=1),
            }
        )
        ongoing = self.env["event.session"].search([("is_ongoing", "=", True)])
        not_ongoing = self.env["event.session"].search([("is_ongoing", "=", False)])
        self.assertFalse(session.is_ongoing)
        self.assertIn(session, not_ongoing)
        self.assertNotIn(session, ongoing)

    def test_event_session_is_finished(self):
        # Case 1: Session is finished
        session = self.env["event.session"].create(
            {
                "event_id": self.event.id,
                "date_begin": fields.Datetime.now() - timedelta(hours=2),
                "date_end": fields.Datetime.now() - timedelta(hours=1),
            }
        )
        finished = self.env["event.session"].search([("is_finished", "=", True)])
        not_finished = self.env["event.session"].search([("is_finished", "=", False)])
        self.assertTrue(session.is_finished)
        self.assertIn(session, finished)
        self.assertNotIn(session, not_finished)
        # Case 2: It isn't
        session.write(
            {
                "date_begin": fields.Datetime.now() + timedelta(days=1),
                "date_end": fields.Datetime.now() + timedelta(days=1, hours=1),
            }
        )
        finished = self.env["event.session"].search([("is_finished", "=", True)])
        not_finished = self.env["event.session"].search([("is_finished", "=", False)])
        self.assertFalse(session.is_finished)
        self.assertIn(session, not_finished)
        self.assertNotIn(session, finished)
