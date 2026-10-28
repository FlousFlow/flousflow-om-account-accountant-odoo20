import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("ff_balance_sheet_formula_info", {
    steps: () => [
        {
            trigger: ".ff_fr_table tbody tr",
            run() {
                const rows = [...document.querySelectorAll(".ff_fr_table tbody tr")].filter((row) =>
                    row.querySelector(".ff_fr_info_button")
                );
                if (!rows.length || rows.some((row) => !row.querySelector(".ff_fr_info_button i[data-icon='info']"))) {
                    throw new Error("The Balance Sheet info icon is missing from one or more report rows.");
                }
                const totalAssetsRow = rows.find((row) => row.textContent.includes("Total ASSETS"));
                if (!totalAssetsRow) {
                    throw new Error("The Total ASSETS report row is missing.");
                }
                totalAssetsRow.querySelector(".ff_fr_info_button").click();
            },
        },
        {
            trigger: ".ff_fr_formula_popover[role='dialog']",
            run() {
                const popover = document.querySelector(".ff_fr_formula_popover");
                const rows = [...popover.querySelectorAll(".ff_fr_formula_row")].map((row) => row.innerText);
                for (const label of ["Engine", "Label", "Formula", "Value"]) {
                    if (!rows.some((row) => row.includes(label))) {
                        throw new Error(`Formula details are missing ${label}.`);
                    }
                }
                const formula = popover.querySelector(".ff_fr_formula_row code")?.textContent.trim();
                if (!formula) {
                    throw new Error("The report formula is empty.");
                }
                if (formula !== "CA.balance + FA.balance + PNCA.balance") {
                    throw new Error(`Total ASSETS formula differs from Enterprise: ${formula}`);
                }
            },
        },
    ],
});
