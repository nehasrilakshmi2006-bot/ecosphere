/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

class EsgDashboard extends Component {
    static template = "ecosphere_esg.EsgDashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            kpis: {
                assets_available: 0,
                assets_allocated: 0,
                active_bookings: 0,
                overdue_returns: 0,
                total_carbon_emissions: 0,
            },
            loading: true,
        });

        onWillStart(async () => {
            await this.loadKpis();
        });
    }

    async loadKpis() {
        const dashboards = await this.orm.searchRead(
            "esg.dashboard",
            [],
            [
                "assets_available",
                "assets_allocated",
                "active_bookings",
                "overdue_returns",
                "total_carbon_emissions",
            ],
            { limit: 1 }
        );
        if (dashboards.length) {
            this.state.kpis = dashboards[0];
        }
        this.state.loading = false;
    }

    openEmissionsGraph() {
        this.action.doAction("ecosphere_esg.action_esg_carbon_emissions_graph");
    }

    openDepartmentRankings() {
        this.action.doAction("ecosphere_esg.action_esg_department_leaderboard");
    }

    get formattedEmissions() {
        const value = this.state.kpis.total_carbon_emissions || 0;
        return value.toFixed(2);
    }
}

registry.category("actions").add("ecosphere_esg_dashboard", EsgDashboard);
