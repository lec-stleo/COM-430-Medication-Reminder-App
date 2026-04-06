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

function renderEmptyState(message) {
    return `<p class="empty-state">${message}</p>`;
}

function renderMedications(medications) {
    if (!medications.length) {
        return renderEmptyState("No medications yet. Add one to start.");
    }

    return medications.map((medication) => `
        <article class="card">
            <h3>${medication.name}</h3>
            <p><strong>Dosage:</strong> ${medication.dosage}</p>
            <p><strong>Status:</strong> ${medication.med_status}</p>
            <p><strong>Photo Path:</strong> ${medication.photo_path || "No reference photo."}</p>
            <p><strong>Notes:</strong> ${medication.notes || "No notes added."}</p>
            <p><strong>Schedules:</strong> ${medication.schedule_count}</p>
        </article>
    `).join("");
}

function renderSchedules(schedules) {
    if (!schedules.length) {
        return renderEmptyState("No schedules yet. Create one after adding a medication.");
    }

    return schedules.map((schedule) => `
        <article class="card">
            <h3>${schedule.medication_name}</h3>
            <p><strong>Dosage:</strong> ${schedule.dosage}</p>
            <p><strong>Date:</strong> ${schedule.scheduled_date}</p>
            <p><strong>Time:</strong> ${schedule.scheduled_time}</p>
            <p><strong>Frequency:</strong> ${schedule.frequency}</p>
            <p><strong>Start Date:</strong> ${schedule.start_date || "Not set"}</p>
            <p><strong>End Date:</strong> ${schedule.end_date || "Not set"}</p>
            <p><strong>Reminder Status:</strong> ${schedule.reminder_status}</p>
            <span class="status ${schedule.status}">${schedule.status}</span>
            <div class="inline-actions">
                <button
                    class="small-button"
                    type="button"
                    data-take-button="${schedule.id}"
                    ${schedule.status !== "pending" ? "disabled" : ""}
                >
                    Mark as Taken
                </button>
                <button
                    class="small-button secondary-action"
                    type="button"
                    data-skip-button="${schedule.id}"
                    ${schedule.status !== "pending" ? "disabled" : ""}
                >
                    Mark as Skipped
                </button>
            </div>
        </article>
    `).join("");
}

function renderHistory(history) {
    if (!history.length) {
        return renderEmptyState("No medication history yet. Mark a schedule as taken to create a log.");
    }

    return history.map((item) => `
        <article class="card">
            <h3>${item.medication_name}</h3>
            <p><strong>Action:</strong> ${item.action}</p>
            <p><strong>Logged At:</strong> ${item.action_at}</p>
            <p><strong>Scheduled For:</strong> ${item.scheduled_date} at ${item.scheduled_time}</p>
            <p><strong>Frequency:</strong> ${item.frequency}</p>
            <p><strong>Notes:</strong> ${item.notes || "No notes recorded."}</p>
        </article>
    `).join("");
}

async function loadDashboard() {
    const welcomeMessage = document.getElementById("welcomeMessage");
    const medicationList = document.getElementById("medicationList");
    const scheduleList = document.getElementById("scheduleList");
    const historyList = document.getElementById("historyList");
    const medicationSelect = document.getElementById("medicationSelect");
    const medicationForm = document.getElementById("medicationForm");
    const scheduleForm = document.getElementById("scheduleForm");
    const logoutButton = document.getElementById("logoutButton");

    async function refreshDashboard() {
        const [me, medications, schedules, history] = await Promise.all([
            apiRequest("/api/auth/me"),
            apiRequest("/api/medications"),
            apiRequest("/api/schedules"),
            apiRequest("/api/history"),
        ]);

        welcomeMessage.textContent = `${me.user.username}'s Medication Overview`;
        medicationList.innerHTML = renderMedications(medications.medications);
        scheduleList.innerHTML = renderSchedules(schedules.schedules);
        historyList.innerHTML = renderHistory(history.history);

        medicationSelect.innerHTML = `
            <option value="">Select medication</option>
            ${medications.medications.map((item) => (
                `<option value="${item.id}">${item.name} (${item.dosage})</option>`
            )).join("")}
        `;

        document.querySelectorAll("[data-take-button]").forEach((button) => {
            button.addEventListener("click", async () => {
                await apiRequest(`/api/schedules/${button.dataset.takeButton}/take`, {
                    method: "PATCH",
                    body: JSON.stringify({}),
                });
                await refreshDashboard();
            });
        });

        document.querySelectorAll("[data-skip-button]").forEach((button) => {
            button.addEventListener("click", async () => {
                await apiRequest(`/api/schedules/${button.dataset.skipButton}/skip`, {
                    method: "PATCH",
                    body: JSON.stringify({}),
                });
                await refreshDashboard();
            });
        });
    }

    medicationForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        await apiRequest("/api/medications", {
            method: "POST",
            body: JSON.stringify(formToJson(medicationForm)),
        });
        medicationForm.reset();
        await refreshDashboard();
    });

    scheduleForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        await apiRequest("/api/schedules", {
            method: "POST",
            body: JSON.stringify(formToJson(scheduleForm)),
        });
        scheduleForm.reset();
        await refreshDashboard();
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
