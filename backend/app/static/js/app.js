async function apiRequest(url, options = {}) {
    // Centralize fetch behavior so every dashboard action gets the same
    // headers, session handling, and JSON error parsing.
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        credentials: "same-origin",
        ...options,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }

    return data;
}

function formToJson(form) {
    return Object.fromEntries(new FormData(form).entries());
}

function setMessage(element, message, isError = false) {
    if (!element) return;
    element.textContent = message || "";
    element.classList.toggle("error", Boolean(isError));
}

function appendTextRow(container, label, value) {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}:`;
    paragraph.append(strong, ` ${value}`);
    container.append(paragraph);
}

function createField(labelText, input) {
    // Forms are built through DOM APIs rather than HTML strings so user values
    // are assigned safely through element properties.
    const label = document.createElement("label");
    label.append(labelText, input);
    return label;
}

function createInputField(type, name, value = "", required = false) {
    const input = document.createElement("input");
    input.type = type;
    input.name = name;
    input.value = value;
    input.required = required;
    return input;
}

function createTextAreaField(name, value = "", rows = 3) {
    const textarea = document.createElement("textarea");
    textarea.name = name;
    textarea.rows = rows;
    textarea.value = value;
    return textarea;
}

function createSelectField(name, options, selectedValue, required = false) {
    const select = document.createElement("select");
    select.name = name;
    select.required = required;

    options.forEach((option) => {
        const optionElement = document.createElement("option");
        optionElement.value = option.value;
        optionElement.textContent = option.label;
        optionElement.selected = option.value === selectedValue;
        select.append(optionElement);
    });

    return select;
}

function createButton(text, className, datasetKey, datasetValue, type = "button") {
    const button = document.createElement("button");
    button.type = type;
    button.className = className;
    button.textContent = text;
    if (datasetKey) {
        button.dataset[datasetKey] = String(datasetValue);
    }
    return button;
}

function createStatusBadge(status) {
    const statusBadge = document.createElement("span");
    statusBadge.className = `status ${status}`;
    statusBadge.textContent = status;
    return statusBadge;
}

function createEmptyState(message) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = message;
    return emptyState;
}

function replaceListContent(container, nodes, emptyMessage) {
    container.replaceChildren(...(nodes.length ? nodes : [createEmptyState(emptyMessage)]));
}

function medicationOptions(medications, selectedId, includePlaceholder = false) {
    const options = [];
    if (includePlaceholder) {
        options.push({ value: "", label: "Select medication" });
    }

    medications.forEach((item) => {
        options.push({
            value: String(item.id),
            label: `${item.name} (${item.dosage})`,
            selected: String(item.id) === String(selectedId),
        });
    });

    return options;
}

function applyOptions(select, options) {
    select.replaceChildren();
    options.forEach((option) => {
        const optionElement = document.createElement("option");
        optionElement.value = option.value;
        optionElement.textContent = option.label;
        optionElement.selected = Boolean(option.selected);
        select.append(optionElement);
    });
}

function createMedicationEditForm(medication) {
    // Inline edit forms keep the dashboard self-contained and easier to review
    // than the earlier prompt()-based editing flow.
    const form = document.createElement("form");
    form.className = "stack inline-form";
    form.hidden = true;
    form.dataset.editMedicationForm = String(medication.id);

    form.append(
        createField(
            "Name",
            createInputField("text", "name", medication.name, true),
        ),
        createField(
            "Dosage",
            createInputField("text", "dosage", medication.dosage, true),
        ),
        createField(
            "Medication Status",
            createSelectField(
                "med_status",
                [
                    { value: "active", label: "Active" },
                    { value: "paused", label: "Paused" },
                    { value: "completed", label: "Completed" },
                ],
                medication.med_status,
                true,
            ),
        ),
        createField(
            "Photo Path",
            createInputField("text", "photo_path", medication.photo_path || ""),
        ),
        createField(
            "Notes",
            createTextAreaField("notes", medication.notes || ""),
        ),
    );

    const actions = document.createElement("div");
    actions.className = "form-actions";
    actions.append(
        createButton("Save Changes", "small-button", null, null, "submit"),
        createButton(
            "Cancel",
            "small-button secondary-action",
            "cancelMedicationEdit",
            medication.id,
        ),
    );

    const inlineMessage = document.createElement("p");
    inlineMessage.className = "form-message";
    inlineMessage.dataset.inlineMessage = `medication-${medication.id}`;

    form.append(actions, inlineMessage);
    return form;
}

function createScheduleEditForm(schedule, medications) {
    const form = document.createElement("form");
    form.className = "stack inline-form";
    form.hidden = true;
    form.dataset.editScheduleForm = String(schedule.id);

    form.append(
        createField(
            "Medication",
            createSelectField(
                "medication_id",
                medicationOptions(medications, schedule.medication_id),
                String(schedule.medication_id),
                true,
            ),
        ),
        createField(
            "Date",
            createInputField("date", "scheduled_date", schedule.scheduled_date, true),
        ),
        createField(
            "Time",
            createInputField("time", "scheduled_time", schedule.scheduled_time, true),
        ),
        createField(
            "Frequency",
            createSelectField(
                "frequency",
                [
                    { value: "daily", label: "Daily" },
                    { value: "weekly", label: "Weekly" },
                    { value: "as-needed", label: "As Needed" },
                    { value: "one-time", label: "One Time" },
                ],
                schedule.frequency,
                true,
            ),
        ),
        createField(
            "Start Date",
            createInputField("date", "start_date", schedule.start_date || ""),
        ),
        createField(
            "End Date",
            createInputField("date", "end_date", schedule.end_date || ""),
        ),
        createField(
            "Reminder Status",
            createSelectField(
                "reminder_status",
                [
                    { value: "enabled", label: "Enabled" },
                    { value: "disabled", label: "Disabled" },
                ],
                schedule.reminder_status,
                true,
            ),
        ),
    );

    const actions = document.createElement("div");
    actions.className = "form-actions";
    actions.append(
        createButton("Save Changes", "small-button", null, null, "submit"),
        createButton(
            "Cancel",
            "small-button secondary-action",
            "cancelScheduleEdit",
            schedule.id,
        ),
    );

    const inlineMessage = document.createElement("p");
    inlineMessage.className = "form-message";
    inlineMessage.dataset.inlineMessage = `schedule-${schedule.id}`;

    form.append(actions, inlineMessage);
    return form;
}

function renderMedicationCards(medications) {
    return medications.map((medication) => {
        const card = document.createElement("article");
        card.className = "card";

        const title = document.createElement("h3");
        title.textContent = medication.name;
        card.append(title);

        appendTextRow(card, "Dosage", medication.dosage);
        appendTextRow(card, "Status", medication.med_status);
        appendTextRow(card, "Photo Path", medication.photo_path || "No reference photo.");
        appendTextRow(card, "Notes", medication.notes || "No notes added.");
        appendTextRow(card, "Schedules", String(medication.schedule_count));

        const actions = document.createElement("div");
        actions.className = "inline-actions";
        actions.append(
            createButton("Edit", "small-button", "toggleMedicationEdit", medication.id),
            createButton(
                "Delete",
                "small-button secondary-action",
                "deleteMedication",
                medication.id,
            ),
        );

        card.append(actions, createMedicationEditForm(medication));
        return card;
    });
}

function renderScheduleCards(schedules, medications) {
    return schedules.map((schedule) => {
        const card = document.createElement("article");
        card.className = "card";

        const title = document.createElement("h3");
        title.textContent = schedule.medication_name;
        card.append(title);

        appendTextRow(card, "Dosage", schedule.dosage);
        appendTextRow(card, "Next Due Date", schedule.scheduled_date);
        appendTextRow(card, "Time", schedule.scheduled_time);
        appendTextRow(card, "Frequency", schedule.frequency);
        appendTextRow(card, "Start Date", schedule.start_date || "Not set");
        appendTextRow(card, "End Date", schedule.end_date || "Not set");
        appendTextRow(card, "Reminder Status", schedule.reminder_status);
        card.append(createStatusBadge(schedule.status));

        const actions = document.createElement("div");
        actions.className = "inline-actions";

        const takeButton = createButton(
            "Mark as Taken",
            "small-button",
            "takeButton",
            schedule.id,
        );
        // Only pending occurrences can be acted on from the dashboard.
        takeButton.disabled = schedule.status !== "pending";

        const skipButton = createButton(
            "Mark as Skipped",
            "small-button secondary-action",
            "skipButton",
            schedule.id,
        );
        skipButton.disabled = schedule.status !== "pending";

        actions.append(
            takeButton,
            createButton("Edit", "small-button", "toggleScheduleEdit", schedule.id),
            skipButton,
            createButton(
                "Delete",
                "small-button secondary-action",
                "deleteSchedule",
                schedule.id,
            ),
        );

        card.append(actions, createScheduleEditForm(schedule, medications));
        return card;
    });
}

function renderUpcomingScheduleCards(schedules) {
    return schedules.map((schedule) => {
        const card = document.createElement("article");
        card.className = "card";

        const title = document.createElement("h3");
        title.textContent = schedule.medication_name;
        card.append(title);

        appendTextRow(
            card,
            "Next Due",
            `${schedule.scheduled_date} at ${schedule.scheduled_time}`,
        );
        appendTextRow(card, "Frequency", schedule.frequency);
        appendTextRow(card, "Status", schedule.status);
        return card;
    });
}

function renderHistoryCards(history) {
    return history.map((item) => {
        const card = document.createElement("article");
        card.className = "card";

        const title = document.createElement("h3");
        title.textContent = item.medication_name;
        card.append(title);

        appendTextRow(card, "Action", item.action);
        appendTextRow(
            card,
            "Occurrence",
            `${item.scheduled_date} at ${item.scheduled_time}`,
        );
        appendTextRow(card, "Logged At", item.action_at);
        appendTextRow(card, "Frequency", item.frequency);
        appendTextRow(card, "Notes", item.notes || "No notes recorded.");
        return card;
    });
}

function renderNotificationCards(notifications) {
    return notifications.map((item) => {
        const card = document.createElement("article");
        card.className = "card";

        const title = document.createElement("h3");
        title.textContent = item.medication_name;
        card.append(title);

        appendTextRow(card, "Type", item.type);
        appendTextRow(
            card,
            "Occurrence",
            `${item.scheduled_date} at ${item.scheduled_time}`,
        );
        appendTextRow(card, "Message", item.message);
        appendTextRow(card, "Sent At", item.sent_at || "Just now");
        return card;
    });
}

async function handleAuthForm(form, mode) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const messageElement = form.querySelector("[data-form-message]");

        try {
            const payload = formToJson(form);
            const result = await apiRequest(`/api/auth/${mode}`, {
                method: "POST",
                body: JSON.stringify(payload),
            });
            setMessage(messageElement, result.message);
            window.location.href = "/dashboard";
        } catch (error) {
            setMessage(messageElement, error.message, true);
        }
    });
}

async function loadDashboard() {
    const welcomeMessage = document.getElementById("welcomeMessage");
    const dashboardMessage = document.getElementById("dashboardMessage");
    const medicationList = document.getElementById("medicationList");
    const scheduleList = document.getElementById("scheduleList");
    const upcomingScheduleList = document.getElementById("upcomingScheduleList");
    const historyList = document.getElementById("historyList");
    const notificationList = document.getElementById("notificationList");
    const medicationSelect = document.getElementById("medicationSelect");
    const medicationForm = document.getElementById("medicationForm");
    const scheduleForm = document.getElementById("scheduleForm");
    const logoutButton = document.getElementById("logoutButton");
    const triggerNotificationsButton = document.getElementById("triggerNotificationsButton");
    const medicationFormMessage = document.querySelector("[data-form-message='medication']");
    const scheduleFormMessage = document.querySelector("[data-form-message='schedule']");

    async function refreshDashboard(message = "") {
        // The dashboard reloads its state from the API after every write so the
        // page reflects the same server-side truth the tests verify.
        const [me, medications, schedules, upcoming, history, notifications] = await Promise.all([
            apiRequest("/api/auth/me"),
            apiRequest("/api/medications"),
            apiRequest("/api/schedules"),
            apiRequest("/api/schedules/upcoming"),
            apiRequest("/api/history"),
            apiRequest("/api/notifications"),
        ]);

        welcomeMessage.textContent = `${me.user.username}'s Medication Overview`;
        setMessage(dashboardMessage, message);

        replaceListContent(
            medicationList,
            renderMedicationCards(medications.medications),
            "No medications yet. Add one to start.",
        );
        replaceListContent(
            scheduleList,
            renderScheduleCards(schedules.schedules, medications.medications),
            "No schedules yet. Create one after adding a medication.",
        );
        replaceListContent(
            upcomingScheduleList,
            renderUpcomingScheduleCards(upcoming.schedules),
            "No upcoming pending schedules.",
        );
        replaceListContent(
            historyList,
            renderHistoryCards(history.history),
            "No medication history yet. Mark a schedule as taken or skipped to create a log.",
        );
        replaceListContent(
            notificationList,
            renderNotificationCards(notifications.notifications),
            "No notifications have been triggered yet.",
        );

        applyOptions(
            medicationSelect,
            medicationOptions(medications.medications, "", true),
        );

        bindDashboardActions();
    }

    function bindDashboardActions() {
        // Event listeners are rebound after each refresh because the card DOM is recreated.
        document.querySelectorAll("[data-toggle-medication-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const form = document.querySelector(
                    `[data-edit-medication-form="${button.dataset.toggleMedicationEdit}"]`,
                );
                form.hidden = false;
            });
        });

        document.querySelectorAll("[data-cancel-medication-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const form = document.querySelector(
                    `[data-edit-medication-form="${button.dataset.cancelMedicationEdit}"]`,
                );
                form.hidden = true;
                setMessage(form.querySelector("[data-inline-message]"), "");
            });
        });

        document.querySelectorAll("[data-edit-medication-form]").forEach((form) => {
            form.addEventListener("submit", async (event) => {
                event.preventDefault();
                const medicationId = form.dataset.editMedicationForm;
                const messageElement = form.querySelector("[data-inline-message]");

                try {
                    await apiRequest(`/api/medications/${medicationId}`, {
                        method: "PUT",
                        body: JSON.stringify(formToJson(form)),
                    });
                    await refreshDashboard("Medication updated successfully.");
                } catch (error) {
                    setMessage(messageElement, error.message, true);
                }
            });
        });

        document.querySelectorAll("[data-delete-medication]").forEach((button) => {
            button.addEventListener("click", async () => {
                try {
                    await apiRequest(`/api/medications/${button.dataset.deleteMedication}`, {
                        method: "DELETE",
                    });
                    await refreshDashboard("Medication deleted successfully.");
                } catch (error) {
                    setMessage(dashboardMessage, error.message, true);
                }
            });
        });

        document.querySelectorAll("[data-toggle-schedule-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const form = document.querySelector(
                    `[data-edit-schedule-form="${button.dataset.toggleScheduleEdit}"]`,
                );
                form.hidden = false;
            });
        });

        document.querySelectorAll("[data-cancel-schedule-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const form = document.querySelector(
                    `[data-edit-schedule-form="${button.dataset.cancelScheduleEdit}"]`,
                );
                form.hidden = true;
                setMessage(form.querySelector("[data-inline-message]"), "");
            });
        });

        document.querySelectorAll("[data-edit-schedule-form]").forEach((form) => {
            form.addEventListener("submit", async (event) => {
                event.preventDefault();
                const scheduleId = form.dataset.editScheduleForm;
                const messageElement = form.querySelector("[data-inline-message]");

                try {
                    await apiRequest(`/api/schedules/${scheduleId}`, {
                        method: "PUT",
                        body: JSON.stringify(formToJson(form)),
                    });
                    await refreshDashboard("Schedule updated successfully.");
                } catch (error) {
                    setMessage(messageElement, error.message, true);
                }
            });
        });

        document.querySelectorAll("[data-delete-schedule]").forEach((button) => {
            button.addEventListener("click", async () => {
                try {
                    await apiRequest(`/api/schedules/${button.dataset.deleteSchedule}`, {
                        method: "DELETE",
                    });
                    await refreshDashboard("Schedule deleted successfully.");
                } catch (error) {
                    setMessage(dashboardMessage, error.message, true);
                }
            });
        });

        document.querySelectorAll("[data-take-button]").forEach((button) => {
            button.addEventListener("click", async () => {
                try {
                    await apiRequest(`/api/schedules/${button.dataset.takeButton}/take`, {
                        method: "PATCH",
                        body: JSON.stringify({}),
                    });
                    await refreshDashboard("Schedule marked as taken.");
                } catch (error) {
                    setMessage(dashboardMessage, error.message, true);
                }
            });
        });

        document.querySelectorAll("[data-skip-button]").forEach((button) => {
            button.addEventListener("click", async () => {
                try {
                    await apiRequest(`/api/schedules/${button.dataset.skipButton}/skip`, {
                        method: "PATCH",
                        body: JSON.stringify({}),
                    });
                    await refreshDashboard("Schedule marked as skipped.");
                } catch (error) {
                    setMessage(dashboardMessage, error.message, true);
                }
            });
        });
    }

    medicationForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        setMessage(medicationFormMessage, "");

        try {
            await apiRequest("/api/medications", {
                method: "POST",
                body: JSON.stringify(formToJson(medicationForm)),
            });
            medicationForm.reset();
            await refreshDashboard("Medication added successfully.");
        } catch (error) {
            setMessage(medicationFormMessage, error.message, true);
        }
    });

    scheduleForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        setMessage(scheduleFormMessage, "");

        try {
            await apiRequest("/api/schedules", {
                method: "POST",
                body: JSON.stringify(formToJson(scheduleForm)),
            });
            scheduleForm.reset();
            await refreshDashboard("Schedule created successfully.");
        } catch (error) {
            setMessage(scheduleFormMessage, error.message, true);
        }
    });

    triggerNotificationsButton.addEventListener("click", async () => {
        try {
            const result = await apiRequest("/api/test/trigger-notifications", { method: "POST" });
            await refreshDashboard(
                `Notification check completed. Triggered ${result.triggered_count} notification(s).`,
            );
        } catch (error) {
            setMessage(dashboardMessage, error.message, true);
        }
    });

    logoutButton.addEventListener("click", async () => {
        await apiRequest("/api/auth/logout", { method: "POST" });
        window.location.href = "/login";
    });

    try {
        await refreshDashboard();
    } catch (_error) {
        window.location.href = "/login";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const authForm = document.querySelector("[data-auth-form]");
    if (authForm) {
        handleAuthForm(authForm, authForm.dataset.authForm);
    }

    if (document.getElementById("medicationForm")) {
        loadDashboard();
    }
});
