async function apiRequest(url, options = {}) {
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

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function renderEmptyState(message) {
    return `<p class="empty-state">${escapeHtml(message)}</p>`;
}

function buildMedicationOptions(medications, selectedId) {
    return medications.map((item) => (
        `<option value="${item.id}" ${item.id === selectedId ? "selected" : ""}>` +
        `${escapeHtml(item.name)} (${escapeHtml(item.dosage)})</option>`
    )).join("");
}

function renderMedications(medications) {
    if (!medications.length) {
        return renderEmptyState("No medications yet. Add one to start.");
    }

    return medications.map((medication) => `
        <article class="card">
            <h3>${escapeHtml(medication.name)}</h3>
            <p><strong>Dosage:</strong> ${escapeHtml(medication.dosage)}</p>
            <p><strong>Status:</strong> ${escapeHtml(medication.med_status)}</p>
            <p><strong>Photo Path:</strong> ${escapeHtml(medication.photo_path || "No reference photo.")}</p>
            <p><strong>Notes:</strong> ${escapeHtml(medication.notes || "No notes added.")}</p>
            <p><strong>Schedules:</strong> ${medication.schedule_count}</p>
            <div class="inline-actions">
                <button class="small-button" type="button" data-toggle-medication-edit="${medication.id}">Edit</button>
                <button class="small-button secondary-action" type="button" data-delete-medication="${medication.id}">Delete</button>
            </div>
            <form class="stack inline-form" data-edit-medication-form="${medication.id}" hidden>
                <label>
                    Name
                    <input type="text" name="name" value="${escapeHtml(medication.name)}" required>
                </label>
                <label>
                    Dosage
                    <input type="text" name="dosage" value="${escapeHtml(medication.dosage)}" required>
                </label>
                <label>
                    Medication Status
                    <select name="med_status" required>
                        <option value="active" ${medication.med_status === "active" ? "selected" : ""}>Active</option>
                        <option value="paused" ${medication.med_status === "paused" ? "selected" : ""}>Paused</option>
                        <option value="completed" ${medication.med_status === "completed" ? "selected" : ""}>Completed</option>
                    </select>
                </label>
                <label>
                    Photo Path
                    <input type="text" name="photo_path" value="${escapeHtml(medication.photo_path || "")}">
                </label>
                <label>
                    Notes
                    <textarea name="notes" rows="3">${escapeHtml(medication.notes || "")}</textarea>
                </label>
                <div class="form-actions">
                    <button class="small-button" type="submit">Save Changes</button>
                    <button class="small-button secondary-action" type="button" data-cancel-medication-edit="${medication.id}">Cancel</button>
                </div>
                <p class="form-message" data-inline-message="medication-${medication.id}"></p>
            </form>
        </article>
    `).join("");
}

function renderSchedules(schedules, medications) {
    if (!schedules.length) {
        return renderEmptyState("No schedules yet. Create one after adding a medication.");
    }

    return schedules.map((schedule) => `
        <article class="card">
            <h3>${escapeHtml(schedule.medication_name)}</h3>
            <p><strong>Dosage:</strong> ${escapeHtml(schedule.dosage)}</p>
            <p><strong>Next Due Date:</strong> ${escapeHtml(schedule.scheduled_date)}</p>
            <p><strong>Time:</strong> ${escapeHtml(schedule.scheduled_time)}</p>
            <p><strong>Frequency:</strong> ${escapeHtml(schedule.frequency)}</p>
            <p><strong>Start Date:</strong> ${escapeHtml(schedule.start_date || "Not set")}</p>
            <p><strong>End Date:</strong> ${escapeHtml(schedule.end_date || "Not set")}</p>
            <p><strong>Reminder Status:</strong> ${escapeHtml(schedule.reminder_status)}</p>
            <span class="status ${escapeHtml(schedule.status)}">${escapeHtml(schedule.status)}</span>
            <div class="inline-actions">
                <button class="small-button" type="button" data-take-button="${schedule.id}" ${schedule.status !== "pending" ? "disabled" : ""}>Mark as Taken</button>
                <button class="small-button" type="button" data-toggle-schedule-edit="${schedule.id}">Edit</button>
                <button class="small-button secondary-action" type="button" data-skip-button="${schedule.id}" ${schedule.status !== "pending" ? "disabled" : ""}>Mark as Skipped</button>
                <button class="small-button secondary-action" type="button" data-delete-schedule="${schedule.id}">Delete</button>
            </div>
            <form class="stack inline-form" data-edit-schedule-form="${schedule.id}" hidden>
                <label>
                    Medication
                    <select name="medication_id" required>
                        ${buildMedicationOptions(medications, schedule.medication_id)}
                    </select>
                </label>
                <label>
                    Date
                    <input type="date" name="scheduled_date" value="${escapeHtml(schedule.scheduled_date)}" required>
                </label>
                <label>
                    Time
                    <input type="time" name="scheduled_time" value="${escapeHtml(schedule.scheduled_time)}" required>
                </label>
                <label>
                    Frequency
                    <select name="frequency" required>
                        <option value="daily" ${schedule.frequency === "daily" ? "selected" : ""}>Daily</option>
                        <option value="weekly" ${schedule.frequency === "weekly" ? "selected" : ""}>Weekly</option>
                        <option value="as-needed" ${schedule.frequency === "as-needed" ? "selected" : ""}>As Needed</option>
                        <option value="one-time" ${schedule.frequency === "one-time" ? "selected" : ""}>One Time</option>
                    </select>
                </label>
                <label>
                    Start Date
                    <input type="date" name="start_date" value="${escapeHtml(schedule.start_date || "")}">
                </label>
                <label>
                    End Date
                    <input type="date" name="end_date" value="${escapeHtml(schedule.end_date || "")}">
                </label>
                <label>
                    Reminder Status
                    <select name="reminder_status" required>
                        <option value="enabled" ${schedule.reminder_status === "enabled" ? "selected" : ""}>Enabled</option>
                        <option value="disabled" ${schedule.reminder_status === "disabled" ? "selected" : ""}>Disabled</option>
                    </select>
                </label>
                <div class="form-actions">
                    <button class="small-button" type="submit">Save Changes</button>
                    <button class="small-button secondary-action" type="button" data-cancel-schedule-edit="${schedule.id}">Cancel</button>
                </div>
                <p class="form-message" data-inline-message="schedule-${schedule.id}"></p>
            </form>
        </article>
    `).join("");
}

function renderUpcomingSchedules(schedules) {
    if (!schedules.length) {
        return renderEmptyState("No upcoming pending schedules.");
    }

    return schedules.map((schedule) => `
        <article class="card">
            <h3>${escapeHtml(schedule.medication_name)}</h3>
            <p><strong>Next Due:</strong> ${escapeHtml(schedule.scheduled_date)} at ${escapeHtml(schedule.scheduled_time)}</p>
            <p><strong>Frequency:</strong> ${escapeHtml(schedule.frequency)}</p>
            <p><strong>Status:</strong> ${escapeHtml(schedule.status)}</p>
        </article>
    `).join("");
}

function renderHistory(history) {
    if (!history.length) {
        return renderEmptyState("No medication history yet. Mark a schedule as taken or skipped to create a log.");
    }

    return history.map((item) => `
        <article class="card">
            <h3>${escapeHtml(item.medication_name)}</h3>
            <p><strong>Action:</strong> ${escapeHtml(item.action)}</p>
            <p><strong>Occurrence:</strong> ${escapeHtml(item.scheduled_date)} at ${escapeHtml(item.scheduled_time)}</p>
            <p><strong>Logged At:</strong> ${escapeHtml(item.action_at)}</p>
            <p><strong>Frequency:</strong> ${escapeHtml(item.frequency)}</p>
            <p><strong>Notes:</strong> ${escapeHtml(item.notes || "No notes recorded.")}</p>
        </article>
    `).join("");
}

function renderNotifications(notifications) {
    if (!notifications.length) {
        return renderEmptyState("No notifications have been triggered yet.");
    }

    return notifications.map((item) => `
        <article class="card">
            <h3>${escapeHtml(item.medication_name)}</h3>
            <p><strong>Type:</strong> ${escapeHtml(item.type)}</p>
            <p><strong>Occurrence:</strong> ${escapeHtml(item.scheduled_date)} at ${escapeHtml(item.scheduled_time)}</p>
            <p><strong>Message:</strong> ${escapeHtml(item.message)}</p>
            <p><strong>Sent At:</strong> ${escapeHtml(item.sent_at || "Just now")}</p>
        </article>
    `).join("");
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
        medicationList.innerHTML = renderMedications(medications.medications);
        scheduleList.innerHTML = renderSchedules(schedules.schedules, medications.medications);
        upcomingScheduleList.innerHTML = renderUpcomingSchedules(upcoming.schedules);
        historyList.innerHTML = renderHistory(history.history);
        notificationList.innerHTML = renderNotifications(notifications.notifications);

        medicationSelect.innerHTML = `
            <option value="">Select medication</option>
            ${buildMedicationOptions(medications.medications)}
        `;

        bindDashboardActions();
    }

    function bindDashboardActions() {
        document.querySelectorAll("[data-toggle-medication-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const form = document.querySelector(`[data-edit-medication-form="${button.dataset.toggleMedicationEdit}"]`);
                form.hidden = false;
            });
        });

        document.querySelectorAll("[data-cancel-medication-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const form = document.querySelector(`[data-edit-medication-form="${button.dataset.cancelMedicationEdit}"]`);
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
                const form = document.querySelector(`[data-edit-schedule-form="${button.dataset.toggleScheduleEdit}"]`);
                form.hidden = false;
            });
        });

        document.querySelectorAll("[data-cancel-schedule-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const form = document.querySelector(`[data-edit-schedule-form="${button.dataset.cancelScheduleEdit}"]`);
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
            await refreshDashboard(`Notification check completed. Triggered ${result.triggered_count} notification(s).`);
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
