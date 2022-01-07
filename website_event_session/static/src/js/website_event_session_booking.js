odoo.define("website_event_session.booking", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const core = require("web.core");
    const time = require("web.time");
    const _t = core._t;

    publicWidget.registry.WebsiteEventSessionBooking = publicWidget.Widget.extend({
        selector: ".o_wevent_session_booking",
        events: {
            "click .session-item": "_onClickSessionItem",
        },

        /**
         * @class
         */
        init() {
            this._super.apply(this, arguments);
            // State
            this.event_id = false;
            this.session_id = false;
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
            // TODO: CHECK
            if (this.editableMode) {
                return res;
            }
            // Find expected dom elements
            this.$datePicker = this.$el.find(".event-session-booking-datepicker");
            this.$sessionSelector = this.$el.find(
                ".event-session-booking-session-selector"
            );
            // Expected dom elements outside of widget scope
            this.$registrationForm = $("#registration_form");
            this.$sessionId = this.$registrationForm.find(
                "input[name='event_session_id']"
            );
            this.$submitBtn = this.$registrationForm.find("button[type='submit']");
            // Page elements
            this.$pages = this.$el.find("li.event-session-booking-section");
            this.$pagesByName = {};
            for (const $page of this.$pages) {
                this.$pagesByName[$page.getAttribute("name")] = $($page);
            }
            this.pages = this.$pages.get().map((el) => el.getAttribute("name"));
            // Get the current event_id
            this.eventId = parseInt(this.$submitBtn.attr("id"));
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
            const data = await this._rpc({
                route: `/event/${this.eventId}/session_dates`,
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
            return await this._rpc({
                route: `/event/${this.eventId}/sessions_for_date`,
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
            this.$el
                .find("li.event-session-booking-section[name='calendar']")
                .removeClass("disable");
        },
        _renderSessionSelector() {
            // TODO: Consider moving this to a QWeb template
            // First, clear sessions
            this.$sessionSelector.empty();
            // If we have no sessions, disable and do nothing
            if (!this.sessions.length) {
                this.$pagesByName.session.addClass("disable");
            } else {
                this.$pagesByName.session.removeClass("disable");
            }
            // Render sessions
            for (const session of this.sessions) {
                // Create element
                const $session = $("<div class='session-item d-block btn'/>");
                $session.attr("data-session-id", session.id);
                $session.html(session.display_name);
                // Compute selected
                if (session.id == this.sessionId) {
                    $session.addClass("btn-primary");
                    $session.attr("selected", true);
                } else {
                    $session.addClass("btn-outline-dark");
                }
                // Compute status
                if (session.seats_limited) {
                    if (session.seats_available <= 0) {
                        $session.attr("title", _t("Full"));
                        $session.tooltip();
                        $session.addClass("disabled");
                    } else {
                        $session.attr(
                            "title",
                            _.str.sprintf(
                                _t("%s available seats"),
                                session.seats_available
                            )
                        );
                        $session.tooltip();
                    }
                } else {
                    // There are unlimited seats here
                    $session.attr("title", _t("Seats available"));
                    $session.tooltip();
                }
                // Add element
                // We use a wrapper to get the proper flex layout with margins
                var $wrapper = $('<div class="session-item-wrapper"/>');
                $wrapper.append($session);
                this.$sessionSelector.append($wrapper);
            }
        },

        // ------------------------
        // Navigation
        // ------------------------

        async selectMonth(year, month) {
            // Launch this in parallel
            const getSessionDatesDeferred = this._getSessionDates(year, month);
            this.$datePicker.addClass("loading");
            // Clear selected date
            await this.clearDate();
            // Load dates
            await getSessionDatesDeferred;
            this.$datePicker.datepicker("refresh");
            this.$datePicker.removeClass("loading");
            // Open page in case it wasn't open
            await this._openPage("calendar");
        },
        async selectDate(dateText) {
            // Launch stuff in parallel
            const getSessionsForDateDeferred = this._getSessionsForDate(dateText);
            // Close and clear sessions
            if (this.collapseClosePrevious) {
                await this._closeAllPages();
            } else {
                await this._closePage("session", true);
            }
            await this.clearSession();
            // Render and show session selector
            const sessionsForDate = await getSessionsForDateDeferred;
            this.sessions = sessionsForDate;
            this.sessionsMap = Object.fromEntries(
                this.sessions.map((session) => [session.id, session])
            );
            this._renderSessionSelector();
            await this._openPage("session");
        },
        async selectSession(sessionId) {
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
        async clearDate() {
            await this._closePage("session");
            await this.clearSession();
            this.sessions = [];
        },
        async clearSession() {
            this.sessionId = false;
            this.$sessionId.val(this.sessionId);
            this.$registrationForm.attr("action", null);
            this._renderSessionSelector();
        },

        // ------------------------
        // Page Navigation
        // ------------------------

        /**
         * @param {String} page
         * @throws Error if not found
         */
        _assertPage(page) {
            if (!Object.keys(this.$pagesByName).includes(page)) {
                throw new Error("Unknown page: " + page);
            }
        },
        /**
         * @param {String} page
         * @returns Array of page names
         */
        _getPagesBefore(page) {
            this._assertPage(page);
            return this.pages.slice(0, this.pages.indexOf(page));
        },
        /**
         * @param {String} page
         * @returns Array of page names
         */
        _getPagesAfter(page) {
            this._assertPage(page);
            return this.pages.slice(this.pages.indexOf(page) + 1);
        },
        /**
         * @param {String} page
         * @param {Boolean} recursive if all pages before should be opened too.
         * @resolves when page is finally closed
         */
        async _openPage(page, recursive) {
            this._assertPage(page);
            const done = $.Deferred();
            const $collapse = this.$pagesByName[page].find(".collapse");
            if (!$collapse.hasClass("show")) {
                $collapse.one("shown.bs.collapse", () => done.resolve());
                $collapse.collapse("show");
            } else {
                done.resolve();
            }
            // Handle recursivity
            if (recursive) {
                const promises = [done];
                for (const pageBefore of this._getPagesBefore(page)) {
                    promises.push(this._openPage(pageBefore));
                }
                return Promise.all(promises);
            }
            return done;
        },
        /**
         * @param {String} page
         * @param {Boolean} recursive if all pages after should be closed too.
         * @resolves when page is finally closed
         */
        async _closePage(page, recursive) {
            this._assertPage(page);
            const done = $.Deferred();
            const $collapse = this.$pagesByName[page].find(".collapse");
            if ($collapse.hasClass("show")) {
                $collapse.one("hidden.bs.collapse", () => done.resolve());
                $collapse.collapse("hide");
            } else {
                done.resolve();
            }
            // Handle recursivity
            if (recursive) {
                const promises = [done];
                for (const pageAfter of this._getPagesAfter(page)) {
                    promises.push(this._closePage(pageAfter));
                }
                return Promise.all(promises);
            }
            return done;
        },
        /**
         * @resolves when all pages are finally closed
         */
        async _closeAllPages() {
            return this._closePage(this.pages[0], true);
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
                const {seats_limited, seats_available} = this.sessionDates[dateStr];
                if (!seats_limited) {
                    return [true, "ui-state-available", _t("Available seats")];
                } else if (seats_available > 0) {
                    return [
                        true,
                        "ui-state-available",
                        _.str.sprintf(_t("%s available seats"), seats_available),
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
            const sId = parseInt($el.attr("data-session-id"));
            if ($el.hasClass("disabled")) {
                return;
            }
            this.selectSession(sId);
        },
    });

    return publicWidget.registry.WebsiteEventSessionBooking;
});
