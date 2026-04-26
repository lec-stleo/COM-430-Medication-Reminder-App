const test = require("node:test");
const assert = require("node:assert/strict");

class FakeElement {
    constructor(tagName) {
        this.tagName = tagName.toUpperCase();
        this.children = [];
        this.dataset = {};
        this.className = "";
        this.textContent = "";
        this.hidden = false;
        this.disabled = false;
        this.required = false;
        this.name = "";
        this.type = "";
        this.value = "";
        this.rows = 0;
    }

    append(...items) {
        items.forEach((item) => {
            this.children.push(item);
            if (typeof item === "string") {
                this.textContent += item;
            } else if (item && typeof item.textContent === "string") {
                this.textContent += item.textContent;
            }
        });
    }

    replaceChildren(...items) {
        this.children = items;
    }

    getAttribute(name) {
        return this[name];
    }
}

global.document = {
    createElement(tagName) {
        return new FakeElement(tagName);
    },
    querySelector(selector) {
        if (selector === 'meta[name="csrf-token"]') {
            return {
                getAttribute(name) {
                    return name === "content" ? "csrf-test-token" : null;
                },
            };
        }
        return null;
    },
    addEventListener() {},
    getElementById() {
        return null;
    },
};

global.window = {};

const {
    apiRequest,
    medicationOptions,
    createMedicationEditForm,
    renderScheduleCards,
} = require("../backend/app/static/js/app.js");

test("apiRequest sends the CSRF token with same-origin credentials", async () => {
    let fetchOptions = null;
    global.fetch = async (_url, options) => {
        fetchOptions = options;
        return {
            ok: true,
            async json() {
                return { message: "ok" };
            },
        };
    };

    await apiRequest("/api/example", {
        method: "POST",
        body: JSON.stringify({ hello: "world" }),
    });

    assert.equal(fetchOptions.credentials, "same-origin");
    assert.equal(fetchOptions.headers["X-CSRF-Token"], "csrf-test-token");
    assert.equal(fetchOptions.headers["Content-Type"], "application/json");
});

test("medicationOptions builds dashboard select labels and placeholder entries", () => {
    const options = medicationOptions(
        [
            { id: 3, name: "Ibuprofen", dosage: "200mg" },
            { id: 7, name: "Aspirin", dosage: "100mg" },
        ],
        7,
        true,
    );

    assert.equal(options[0].label, "Select medication");
    assert.equal(options[2].selected, true);
    assert.equal(options[2].label, "Aspirin (100mg)");
});

test("createMedicationEditForm creates a hidden inline form tied to the medication id", () => {
    const form = createMedicationEditForm({
        id: 12,
        name: "Ibuprofen",
        dosage: "200mg",
        med_status: "active",
        photo_path: "",
        notes: "Take with food",
    });

    assert.equal(form.hidden, true);
    assert.equal(form.dataset.editMedicationForm, "12");
    assert.equal(form.children.length >= 6, true);
});

test("renderScheduleCards disables action buttons for completed occurrences", () => {
    const [card] = renderScheduleCards(
        [
            {
                id: 9,
                medication_id: 3,
                medication_name: "Aspirin",
                dosage: "100mg",
                scheduled_date: "2026-04-10",
                scheduled_time: "09:00",
                frequency: "one-time",
                start_date: "2026-04-10",
                end_date: "",
                reminder_status: "enabled",
                status: "taken",
            },
        ],
        [{ id: 3, name: "Aspirin", dosage: "100mg" }],
    );

    const actions = card.children.find(
        (child) => child && child.className === "inline-actions",
    );
    const takeButton = actions.children[0];
    const skipButton = actions.children[2];

    assert.equal(takeButton.disabled, true);
    assert.equal(skipButton.disabled, true);
});
