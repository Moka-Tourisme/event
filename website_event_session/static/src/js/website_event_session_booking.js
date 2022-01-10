/*
    Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("website_event_session.booking", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const core = require("web.core");
    const time = require("web.time");
    const _t = core._t;

    publicWidget.registry.WebsiteEventSessionBooking = publicWidget.Widget.extend({
        selector: ".js_wevent_session_booking",
        xmlDependencies: [
            "/website_event_session/static/src/xml/website_event_session_booking.xml",
        ],
        events: {
            "change input[name='event_session_id']": "_onClickSessionItem",
        },

        /**
         * @class
         */
        init() {
            this._super.apply(this, arguments);
            // Cached data
            this.sessionDates = {};
            this.sessions = [];
            this.sessionsMap = {};
        },

        /**
         * @override
         */
        start() {
            const res = this._super.apply(this, arguments);
            // Don't render if we're on editable mode
            if (this.editableMode) {
                return res;
            }
            // Find expected dom elements
            this.$datePicker = this.$el.find(".js_wevent_session_booking_datepicker");
            this.$sessionSelector = this.$el.find(
                ".js_wevent_session_booking_sessionpicker"
            );
            // Expected dom elements outside of widget scope
            this.$registrationForm = $("#registration_form");
            this.$sessionId = this.$registrationForm.find(
                "input[name='event_session_id']"
            );
            // Load current month and show calendar
            this._renderCalendar();
            const today = new Date();
            this.selectMonth(today.getFullYear(), today.getMonth() + 1);
            return res;
        },

        // --------------------------
        // Server Data Loading
        // --------------------------

        /**
         * Gets session dates for a given year, month
         *
         * @param {Number} year
         * @param {Number} month
         * @returns session dates
         */
        async _getSessionDates(year, month) {
            const eventId = parseInt(this.$el.attr("data-event-id"));
            const data = await this._rpc({
                route: `/event/${eventId}/session_dates`,
                params: {
                    date_begin: new Date(year, month - 1, 0),
                    date_end: new Date(year, month, 0),
                },
            });
            // Update our internal cache
            Object.assign(this.sessionDates, data);
            return data;
        },
        /**
         * Gets sessions for a given date
         *
         * @param {String} dateText in YYYY-MM-DD format
         * @returns sessions data
         */
        async _getSessionsForDate(dateText) {
            const eventId = parseInt(this.$el.attr("data-event-id"));
            return await this._rpc({
                route: `/event/${eventId}/sessions_for_date`,
                params: {
                    date: dateText,
                },
            });
        },

        // --------------------------
        // Rendering
        // --------------------------

        _renderCalendar() {
            this.$datePicker.datepicker({
                calendarWeeks: true,
                minDate: 0,
                locale: moment.locale(),
                format: time.getLangDatetimeFormat(),
                dateFormat: "yy-mm-dd",
                beforeShowDay: this._onDatepickerBeforeShowDay.bind(this),
                onChangeMonthYear: this._onDatepickerChangeMonthYear.bind(this),
                onSelect: this._onDatepickerSelect.bind(this),
            });
        },
        _renderSessionSelector() {
            this.$sessionSelector.html(
                core.qweb.render("event_session_selector", {widget: this})
            );
        },

        // ------------------------
        // Navigation
        // ------------------------

        async selectMonth(year, month) {
            this.$datePicker.addClass("loading");
            await this._getSessionDates(year, month);
            this.$datePicker.datepicker("refresh");
            this.$datePicker.removeClass("loading");
        },
        async selectDate(dateText) {
            this.clearSession();
            // Render and show session selector
            this.$sessionSelector.addClass("loading");
            this.sessions = await this._getSessionsForDate(dateText);
            this._renderSessionSelector();
            this.$sessionSelector.removeClass("loading");
        },
        selectSession(sessionId) {
            // Set internal and form session id
            this.sessionId = sessionId;
            this.$sessionId.val(this.sessionId);
            // Recompute buttons statuses
            this._renderSessionSelector();
            // Trigger change event on registration form, to update the registration status
            this.$registrationForm.attr(
                "action",
                `/event/session/${this.sessionId}/registration/new`
            );
            this.$registrationForm.find(".custom-select").trigger("change");
        },
        clearDate() {
            this.sessions = [];
            this.clearSession();
        },
        clearSession() {
            this.sessionId = false;
            this.$sessionId.val(this.sessionId);
            this.$registrationForm.attr("action", null);
            this._renderSessionSelector();
        },

        // --------------------------
        // Event Handlers
        // --------------------------

        /**
         * @event
         */
        _onDatepickerBeforeShowDay(date) {
            const dateStr = moment(date).format("YYYY-MM-DD");
            if (this.sessionDates[dateStr] !== undefined) {
                const {sessions_count, seats_limited, seats_available} =
                    this.sessionDates[dateStr];
                if (!seats_limited || seats_available > 0) {
                    return [
                        true,
                        "ui-state-available",
                        _.str.sprintf(_t("%s sessions"), sessions_count),
                    ];
                }
                return [true, "ui-state-not-available", _t("Full")];
            }
            return [false];
        },
        /**
         * @event
         */
        _onDatepickerChangeMonthYear(year, month) {
            return this.selectMonth(year, month);
        },
        /**
         * @event
         */
        _onDatepickerSelect(dateText) {
            this.selectDate(dateText);
        },
        /**
         * @event
         */
        _onClickSessionItem(event) {
            const $el = $(event.currentTarget);
            const sId = parseInt($el.val());
            this.selectSession(sId);
        },
    });

    return publicWidget.registry.WebsiteEventSessionBooking;
});
