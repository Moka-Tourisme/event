# Copyright 2017-19 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2021 Moka Tourisme (https://www.mokatourisme.fr).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo.exceptions import ValidationError

from .common import CommonEventSessionCase


class TestEventSessionCreateWizard(CommonEventSessionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create(
            {"name": "Test Event", "use_sessions": True}
        )
        cls.timeslot_16_00 = cls.env.ref("event_session.timeslot_16_00")
        cls.timeslot_20_00 = cls.env.ref("event_session.timeslot_20_00")

    def test_timeslot_name_create(self):
        Timeslot = self.env["event.session.timeslot"]
        # Case 1: Simple case
        timeslot_id, __ = Timeslot.name_create("23:00")
        timeslot = Timeslot.browse(timeslot_id)
        self.assertEqual(timeslot.time, 23.00)
        # Case 2: float case
        timeslot_id, __ = Timeslot.name_create("23:30")
        timeslot = Timeslot.browse(timeslot_id)
        self.assertEqual(timeslot.time, 23.50)
        # Case 3: invalid
        msg = "The timeslot has to be defined in HH:MM format"
        with self.assertRaisesRegex(ValidationError, msg):
            Timeslot.name_create("25:30")
        # Case 4: invalid
        msg = "The timeslot has to be defined in HH:MM format"
        with self.assertRaisesRegex(ValidationError, msg):
            Timeslot.name_create("22:70")

    def test_session_create_wizard_weekly_01(self):
        """Mondays at 16:00 and 20:00, for whole Jan 2022

        ╔════════════════════╗
        ║ January ░░░░░ 2022 ║
        ╟──┬──┬──┬──┬──┬──┬──╢
        ║░░│░░│░░│░░│░░│░░│  ║
        ╟──╔══╗──┼──┼──┼──┼──╢
        ║  ║03║  │  │  │  │  ║
        ╟──╠══╣──┼──┼──┼──┼──╢
        ║  ║10║  │  │  │  │  ║
        ╟──╠══╣──┼──┼──┼──┼──╢
        ║  ║17║  │  │  │  │  ║
        ╟──╠══╣──┼──┼──┼──┼──╢
        ║  ║24║  │  │  │  │  ║
        ╟──╠══╣──┼──┼──┼──┼──╢
        ║  ║31║░░│░░│░░│░░│░░║
        ╚══╚══╝══╧══╧══╧══╧══╝
        """
        self.assertSessionDates(
            self._wizard_generate_sessions(
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
            ),
            [
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
            ],
        )

    def test_session_create_wizard_weekly_02(self):
        """Mondays, Wednesdays and Fridays at 20:00, every 2 weeks for a Feb 2022

        ╔════════════════════╗
        ║ February ░░░░ 2022 ║
        ╟──┬──┬──╔══╗──╔══╗──╢
        ║░░│░░│  ║02║  ║04║  ║
        ╟──┼──┼──╚══╝──╚══╝──╢
        ║  │  │  │  │  │  │  ║
        ╟──╔══╗──╔══╗──╔══╗──╢
        ║  ║14║  ║16║  ║18║  ║
        ╟──╚══╝──╚══╝──╚══╝──╢
        ║  │  │  │  │  │  │  ║
        ╟──╔══╗──┼──┼──┼──┼──╢
        ║  ║28║░░│░░│░░│░░│░░║
        ╚══╚══╝══╧══╧══╧══╧══╝
        """
        self.assertSessionDates(
            self._wizard_generate_sessions(
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
            ),
            [
                "2022-02-02 20:00:00",
                "2022-02-04 20:00:00",
                "2022-02-14 20:00:00",
                "2022-02-16 20:00:00",
                "2022-02-18 20:00:00",
                "2022-02-28 20:00:00",
            ],
        )

    def test_session_create_wizard_monthly(self):
        """Last sunday of each month at 16:00, from March 2022 to May 2022"""
        self.assertSessionDates(
            self._wizard_generate_sessions(
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
            ),
            [
                "2022-03-27 16:00:00",
                "2022-04-24 16:00:00",
                "2022-05-29 16:00:00",
            ],
        )
