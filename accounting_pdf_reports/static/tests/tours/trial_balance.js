import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("ff_trial_balance_controls", {
    steps: () => [
        { trigger: ".ff_tb_period_picker button", run: "click" },
        {
            trigger: ".ff_tb_period_menu.show",
            run() {
                const labels = [...this.anchor.querySelectorAll(".ff_tb_period_option > .dropdown-item")]
                    .map((item) => item.textContent.trim());
                if (labels.join(",") !== "Month,Quarter,Fiscal Year") {
                    throw new Error(`Unexpected Trial Balance periods: ${labels.join(", ")}`);
                }
            },
        },
        { trigger: ".ff_tb_period_option:nth-child(2) .dropdown-item", run: "click" },
        { trigger: ".ff_tb_period_option:nth-child(2) .dropdown-item.active" },
        { trigger: ".ff_tb_period_menu > .dropdown-item", run: "click" },
        { trigger: ".ff_tb_period_menu input[aria-label='Start Date']" },
        { trigger: ".ff_tb_period_picker button", run: "click" },
        {
            trigger: ".ff_trial_balance button",
            run() {
                const button = [...document.querySelectorAll(".ff_trial_balance button")]
                    .find((item) => item.textContent.trim() === "Comparison");
                if (!button) throw new Error("Comparison control is missing.");
                button.click();
            },
        },
        { trigger: ".ff_tb_table thead tr:nth-child(2) th:nth-child(8)", run() {
            if (this.anchor.textContent.trim() !== "Previous Balance") {
                throw new Error("Comparison columns did not appear.");
            }
        } },
    ],
});
