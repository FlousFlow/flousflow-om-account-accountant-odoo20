import { registry } from "@web/core/registry";

async function waitFor(assertion, message) {
    const started = Date.now();
    while (Date.now() - started < 10000) {
        if (assertion()) {
            return;
        }
        await new Promise((resolve) => setTimeout(resolve, 50));
    }
    throw new Error(message);
}

function periodLabel() {
    return document.querySelector(".ff_journal_audit_period_picker > button")?.innerText.trim() || "";
}

async function fillDateAndWait(input, value) {
    input.value = value;
    input.dispatchEvent(new Event("change", { bubbles: true }));
    await new Promise((resolve, reject) => {
        const started = Date.now();
        const check = () => {
            const loading = document.querySelector(".o_ff_journal_audit .fa-spinner.fa-spin");
            if (!loading) {
                resolve();
            } else if (Date.now() - started > 10000) {
                reject(new Error("Journal Audit period reload did not finish."));
            } else {
                setTimeout(check, 50);
            }
        };
        setTimeout(check, 50);
    });
}

registry.category("web_tour.tours").add("ff_journal_audit_period_filter", {
    steps: () => [
        { trigger: ".o_ff_journal_audit .ff_journal_audit_table" },
        { trigger: ".ff_journal_audit_period_picker > button", run: "click" },
        {
            trigger: ".ff_journal_audit_period_option:nth-child(1) .dropdown-item",
            run: "click",
        },
        {
            trigger: ".ff_journal_audit_period_picker > button",
            async run() {
                await waitFor(
                    () => /January|February|March|April|May|June|July|August|September|October|November|December/i.test(periodLabel()),
                    `Month period was not selected. Current label: ${periodLabel() || "missing"}`
                );
            },
        },
        { trigger: ".ff_journal_audit_period_picker > button", run: "click" },
        {
            trigger: ".ff_journal_audit_period_option:nth-child(2) .dropdown-item",
            run: "click",
        },
        {
            trigger: ".ff_journal_audit_period_picker > button",
            async run() {
                await waitFor(
                    () => /Q[1-4]/.test(periodLabel()),
                    `Quarter period was not selected. Current label: ${periodLabel() || "missing"}`
                );
                window.ffJournalAuditQuarterBefore = periodLabel();
            },
        },
        {
            trigger: ".ff_journal_audit_period_picker > button",
            run: "click",
        },
        {
            trigger: ".ff_journal_audit_period_option:nth-child(2) button[aria-label='Next quarter']",
            run: "click",
        },
        {
            trigger: ".o_ff_journal_audit .ff_journal_audit_table",
            async run() {
                await waitFor(() => {
                    const current = periodLabel();
                    return current && current !== window.ffJournalAuditQuarterBefore;
                }, "Quarter navigation did not change the report period");
            },
        },
        {
            trigger: ".ff_journal_audit_period_option:nth-child(3) .dropdown-item",
            run: "click",
        },
        {
            trigger: ".o_ff_journal_audit .ff_journal_audit_table",
            async run() {
                await waitFor(
                    () => /^\d{4}(?:–\d{4})?$/.test(periodLabel()),
                    `Fiscal year period was not selected. Current label: ${periodLabel() || "missing"}`
                );
            },
        },
        { trigger: ".ff_journal_audit_period_picker > button", run: "click" },
        {
            trigger: ".ff_journal_audit_custom_period input[aria-label='Start Date']",
            run: async function () {
                await fillDateAndWait(this.anchor, "2026-01-10");
            },
        },
        {
            trigger: ".ff_journal_audit_custom_period input[aria-label='End Date']",
            run: async function () {
                await fillDateAndWait(this.anchor, "2026-02-20");
            },
        },
        {
            trigger: ".o_ff_journal_audit .ff_journal_audit_table",
            run() {
                const dates = [...document.querySelectorAll(".ff_journal_audit_custom_period input")].map((input) => input.value);
                if (dates[0] !== "2026-01-10" || dates[1] !== "2026-02-20") {
                    throw new Error(`Custom dates were not applied: ${dates.join(" to ")}`);
                }
            },
        },
    ],
});
