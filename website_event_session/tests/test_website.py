# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserDemo


@tagged("post_install", "-at_install")
class TestUi(HttpCaseWithUserDemo):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env.ref("event_session.event_event_007")

    def test_01_booking_tour_admin(self):
        previous_registrations = self.event.registration_ids
        self.start_tour("/", "website_event_session_tour_booking", login="admin")
        new_registrations = self.event.registration_ids - previous_registrations
        self.assertEqual(len(new_registrations), 1)
        self.assertEqual(
            new_registrations.session_id,
            self.event.session_ids[0],
        )

    def test_01_booking_tour_demo(self):
        previous_registrations = self.event.registration_ids
        self.start_tour("/", "website_event_session_tour_booking", login="demo")
        new_registrations = self.event.registration_ids - previous_registrations
        self.assertEqual(len(new_registrations), 1)
        self.assertEqual(
            new_registrations.session_id,
            self.event.session_ids[0],
        )
