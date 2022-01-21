/* eslint-disable no-empty-function */
odoo.define("website_event_session.tour_booking", function (require) {
    "use strict";

    const tour = require("web_tour.tour");

    tour.register(
        "website_event_session_tour_booking",
        {
            test: true,
            url: "/events",
        },
        [
            {
                content: "Select demo event",
                trigger: "article h5.card-title span:contains('007: No Time to Die')",
            },
            {
                content: "Open the datepicker",
                trigger: "#registration_form *[name='event_session_date']",
            },
            {
                content: "Select the first available date",
                trigger: ".ui-event-session-datepicker .ui-state-available:first",
            },
            {
                content: "Select the first available time",
                trigger:
                    "#registration_form *[name=event_session_id] option[value]:first",
            },
            {
                content: "Add one ticket",
                trigger: ".event-session-tickets select:first",
                run: "text 1",
            },
            {
                content: "Click 'Register' button",
                trigger: "#registration_form button[type=submit]",
            },
            {
                content: "Submit the attendee details form",
                trigger: ".js_website_submit_form button[type=submit]",
            },
            {
                content: "Wait until confirmation page is loaded",
                trigger: "h3:contains('Registration confirmed!')",
                run: function () {},
            },
        ]
    );
});
