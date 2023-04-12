# Copyright 2022 Associazione Odoo Italia (<http://www.odoo-italia.org>)
# Copyright 2022 MKT Srl (<www.mkt.it>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "ITA - Bilancio riclassificato EU",
    "version": "14.0.1.0.0",
    "category": "Localization/Italy",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "MKT Srl, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-italy",
    "mantainers": ["mktsrl"],
    "depends": [
        "account",
        "l10n_it_rea",
        "l10n_it_fiscalcode",
        "report_xlsx",
    ],
    "data": [
        "security/account_balance_eu.xml",
        "views/account_balance_eu_view.xml",
        "data/account.balance.eu.csv",
        "data/account_balance_eu_reclassification.xml",
        "wizards/account_balance_eu_wizard.xml",
        "report/account_balance_eu_report.xml",
    ],
    "application": False,
    "installable": True,
}
