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
        selector: ".o_wevent_session_js_booking",
        xmlDependencies: [
            "/website_event_session/static/src/xml/website_event_session_booking.xml",
        ],
        events: {
            "change input[name='event_session_date']": "_onChangeDate",
            "change *[name='event_session_id']": "_onChangeSession",
            "change .ticket-select": "_onTicketQuantityChange",
            "click button[type='submit']": "_onSubmit",
        },

        /**
         * @class
         */
        init() {
            this._super.apply(this, arguments);
            // Cached data
            this.sessionDates = {};
            this.sessions = [];
            this.tickets = [];
        },

        /**
         * @override
         */
        start() {
            const res = this._super.apply(this, arguments);
            // Don't render if we're on editable mode
            // TODO: Analyze if we need cleaning to avoid breaking website views
            if (this.editableMode) {
                return res;
            }
            // Find expected dom elements
            this.$datePicker = this.$el.find("input[name='event_session_date']");
            this.$sessionId = this.$el.find("*[name='event_session_id']");
            this.$tickets = this.$el.find(".event-session-tickets");
            this.$submit = this.$el.find("button[type='submit']");
            // Load current month and show calendar
            this.$datePicker.val(_t("Select a date..."));
            this._renderCalendar();
            const today = new Date();
            this.selectMonth(today.getFullYear(), today.getMonth() + 1);
            this.clearSession();
            return res;
        },

        currentDate() {
            return this.$datePicker.val();
        },
        sessionId() {
            return parseInt(this.$sessionId.val(), 10);
        },
        eventId() {
            return parseInt(this.$el.attr("data-event-id"), 10);
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
            const data = await this._rpc({
                route: `/event/${this.eventId()}/session_dates`,
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
         * @param {Date} date
         * @returns sessions data
         */
        async _getSessionsForDate(date) {
            return await this._rpc({
                route: `/event/${this.eventId()}/sessions_for_date`,
                params: {
                    date: date,
                },
            });
        },

        _getSessionTicketFields() {
            return ["id", "name", "description"];
        },

        /**
         * Gets session tickets
         *
         * @param {Number} sessionId
         * @returns session tickets
         */
        async _getSessionTickets(sessionId) {
            return await this._rpc({
                route: `/event/session/${sessionId}/tickets`,
            });
        },

        // --------------------------
        // Rendering
        // --------------------------

        _renderCalendar() {
            this.$datePicker.datepicker({
                autoSize: true,
                calendarWeeks: true,
                minDate: 0,
                locale: moment.locale(),
                format: time.getLangDatetimeFormat(),
                beforeShow: (input, dp) => {
                    dp.dpDiv.addClass("ui-event-session-datepicker");
                },
                beforeShowDay: this._onDatepickerBeforeShowDay.bind(this),
                onChangeMonthYear: this._onDatepickerChangeMonthYear.bind(this),
            });
        },
        _renderSessionSelector() {
            this.$sessionId.html(
                core.qweb.render("event_session_selector", {widget: this})
            );
            this.$sessionId.prop("disabled", this.sessions.length === 0);
        },
        _renderTickets() {
            // Render tickets selector
            this.$tickets.html(
                core.qweb.render("event_session_tickets", {widget: this})
            );
            // Dynamic collapse animation
            this.$tickets.collapse(this.tickets.length ? "show" : "hide");
            // Trigger to recompute the submit button state
            this._onTicketQuantityChange();
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
        async selectDate(date) {
            this.clearSession();
            // Render and show session selector
            this.$sessionId.addClass("loading");
            this.sessions = await this._getSessionsForDate(date);
            this._renderSessionSelector();
            this.$sessionId.removeClass("loading");
        },
        async selectSession(sessionId) {
            // Update input value
            this.$sessionId.val(sessionId);
            // Get tickets and render them
            this.$tickets.addClass("loading");
            this.tickets = await this._getSessionTickets(sessionId);
            this.$tickets.removeClass("loading");
            this._renderTickets();
        },
        clearDate() {
            this.sessions = [];
            this.clearSession();
        },
        clearSession() {
            this.$sessionId.val(false);
            this._renderSessionSelector();
            this.clearTickets();
        },
        clearTickets() {
            this.tickets = [];
            this.$tickets.collapse("hide");
            this._renderTickets();
        },

        // --------------------------
        // Other
        // --------------------------

        /**
         * @private
         * @returns {Number}
         */
        _getTotalTicketCount() {
            let ticketCount = 0;
            this.$tickets
                .find(".custom-select")
                .each((i, el) => (ticketCount += parseInt(el.value, 10)));
            return ticketCount;
        },

        // --------------------------
        // Event Handlers
        // --------------------------

        /**
         * @param {Date} date
         * @event
         * @returns {Array} datepicker expected data
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
         * @param {Number} year
         * @param {Number} month
         * @event
         */
        _onDatepickerChangeMonthYear(year, month) {
            this.selectMonth(year, month);
        },
        /**
         * @param {Event} event
         * @event
         */
        _onChangeDate(event) {
            const date = $(event.currentTarget).datepicker("getDate");
            this.selectDate(date);
        },
        /**
         * @param {Event} event
         * @event
         */
        _onChangeSession(event) {
            const sessionId = event.currentTarget.value;
            this.selectSession(sessionId);
        },

        /**
         * @event
         */
        _onTicketQuantityChange() {
            const enabled = this.sessionId() && this._getTotalTicketCount() > 0;
            this.$submit.attr("disabled", !enabled);
        },
    });

    return publicWidget.registry.WebsiteEventSessionBooking;
});
