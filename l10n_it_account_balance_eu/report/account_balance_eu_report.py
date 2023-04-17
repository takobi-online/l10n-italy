from datetime import datetime

from odoo import _, models


def print_date(str_date):
    return datetime.strptime(str_date, "%Y-%m-%d").strftime("%d/%m/%Y")


class BalanceEuXlsxReport(models.AbstractModel):
    _name = "report.l10n_it_account_balance_eu.balance_eu_xlsx_report"
    _description = "Export EU Balance in XLSX format"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, record_data):
        balance_ue_data = self.env["account.balance.eu"].cal_balance_ue_data(data)
        sheet = workbook.add_worksheet(_("Balance EU"))
        st_bold18 = workbook.add_format({"bold": True, "font_size": 18})
        sheet.write(0, 0, data["company_name"], st_bold18)
        sheet.set_row(0, 28)
        sheet.write(1, 0, data["address"] + " - " + data["city"])
        sheet.write(2, 0, _("Social capital Euro ") + str(data["rea_capital"]))
        sheet.write(4, 0, data["name"], st_bold18)
        sheet.set_row(4, 28)
        sheet.write(
            5,
            0,
            _("from")
            + " "
            + print_date(data["date_from"])
            + " "
            + _("to")
            + " "
            + print_date(data["date_to"]),
        )
        str_opz = "(" + _("Values show as") + ": "
        if data["values_precision"] == "d":
            str_opz += _("2 decimals Euro")
        else:  # "u"
            str_opz += _("euro units")
        str_opz += " / " + _("Hide account with amount 0") + ": "
        if data["hide_acc_amount_0"]:
            str_opz += _("YES")
        else:
            str_opz += _("NO")
        str_opz += " / " + _("Use only posted registration") + ": "
        if data["only_posted_move"]:
            str_opz += _("YES")
        else:
            str_opz += _("NO")
        str_opz += " / " + _("Ignore closing registration") + ": "
        if data["ignore_closing_move"]:
            str_opz += _("YES")
        else:
            str_opz += _("NO")
        str_opz += ")"
        st_bold9 = workbook.add_format({"font_size": 9})
        sheet.write(6, 0, str_opz, st_bold9)

        col_title_style = workbook.add_format({"fg_color": "#729fcf"})
        col_title_center_style = workbook.add_format(
            {"fg_color": "#729fcf", "align": "center"}
        )
        row_table_titles = 8
        sheet.write(row_table_titles, 0, _("Description"), col_title_style)
        sheet.write(row_table_titles, 1, _("Code"), col_title_style)
        sheet.write(row_table_titles, 2, str(data["year"]), col_title_center_style)
        st_des = workbook.add_format({"num_format": "@"})
        st_account = workbook.add_format(
            {"italic": True, "font_size": 9, "fg_color": "#efefef"}
        )
        st_acc_code = workbook.add_format(
            {"italic": True, "font_size": 9, "align": "right", "fg_color": "#efefef"}
        )
        if data["values_precision"] == "d":
            amount_style = workbook.add_format({"num_format": "#,##0.00"})
            st_account_amount = workbook.add_format(
                {
                    "italic": True,
                    "font_size": 9,
                    "fg_color": "#efefef",
                    "num_format": "#,##0.00",
                }
            )
        elif data["values_precision"] == "u":
            amount_style = workbook.add_format({"num_format": "#,##0"})
            st_account_amount = workbook.add_format(
                {"font_size": 9, "fg_color": "#efefef", "num_format": "#,##0"}
            )
        row = row_table_titles + 1
        max_l_descr = 0
        max_l_importo = 0
        for line in balance_ue_data["balance_ue_lines"]:
            code = line["code"]
            length = len(code[code.find(".") :])
            desc = ""
            for _c in range(length - 1):
                desc += " "
            desc += line["desc"]
            sheet.write(row, 0, desc, st_des)
            sheet.write(row, 1, code)
            sheet.write(row, 2, line["amount"], amount_style)
            row += 1
            if len(desc) > max_l_descr:
                max_l_descr = len(desc)
            length = len(str(line["amount"]))
            if length > max_l_importo:
                max_l_importo = length
            for acc in line["accounts"]:
                sheet.write(row, 0, "             " + acc["desc"], st_account)
                sheet.write(row, 1, acc["code"], st_acc_code)
                sheet.write(row, 2, acc["amount"], st_account_amount)
                row += 1
        sheet.set_column(0, 0, max_l_descr)
        sheet.set_column(2, 2, max_l_importo + 2)


class BalanceEuXBRLReport(models.AbstractModel):
    _name = "report.l10n_it_account_balance_eu.balance_eu_xbrl_report"
    _description = "Export EU Balance in XBRL format"
    _inherit = "report.report_xml.abstract"

    def get_xbrl_data_tag(self, str_field, str_year, value, decimal_precision=-1):
        complete_field = "itcc-ci:" + str_field
        if decimal_precision >= 0:
            altri_attr = ' unitRef="eur" decimals="{}"'.format(decimal_precision)
            value = f"{value:.{decimal_precision}f}"
        else:
            altri_attr = ""
        return """
    <{} contextRef="{}"{}>{}</{}>""".format(
            complete_field, str_year, altri_attr, value, complete_field
        )

    def get_balance_line_tags(
        self, balance_line_id, balance_ue_lines, str_year, decimal_precision
    ):
        result = ""
        for child in balance_line_id.child_ids:
            result += self.get_balance_line_tags(
                child, balance_ue_lines, str_year, decimal_precision
            )
        if balance_line_id.tag_xbrl:
            amount = None
            i = 0
            while (amount is None) and (i < len(balance_ue_lines)):
                if balance_ue_lines[i]["code"] == balance_line_id["code"]:
                    amount = balance_ue_lines[i]["amount"]
                i += 1
            if amount is not None:
                result += self.get_xbrl_data_tag(
                    balance_line_id.tag_xbrl, str_year, amount, decimal_precision
                )
        return result

    def generate_report(self, ir_report, docids, data=None):
        balance_form_data = data
        balance_ue_data = self.env["account.balance.eu"].cal_balance_ue_data(
            balance_form_data
        )
        i_year = "i_" + str(balance_form_data["year"])
        d_year = "d_" + str(balance_form_data["year"])
        xbrl = """<?xml version = "1.0" encoding = "UTF-8"?>
        <xbrl xmlns="http://www.xbrl.org/2003/instance"
                xmlns:link="http://www.xbrl.org/2003/linkbase"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:iso4217="http://www.xbrl.org/2003/iso4217"
                xmlns:xbrli="http://www.xbrl.org/2003/instance"
                xmlns:itcc-ci="http://www.infocamere.it/itnn/fr/itcc/ci/2018-11-04"
                xmlns:itcc-ci-ese="http://www.infocamere.it/itnn/fr/itcc/ci/ese/2018-11-04">
            <link:schemaRef xlink:type="simple"
                xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"
                xlink:href="itcc-ci-ese-2018-11-04.xsd"/>"""

        xbrl += """
            <context id="{}">
                <entity>
                  <identifier scheme="http://www.infocamere.it">{}</identifier>
                </entity>
                <period>
                  <instant>{}</instant>
                </period>
                <scenario>
                  <itcc-ci-ese:scen>Depositato</itcc-ci-ese:scen>
                </scenario>
            </context>""".format(
            i_year,
            balance_form_data["fiscalcode"],
            balance_form_data["date_to"],
        )

        xbrl += """
            <context id="{}">
                <entity>
                  <identifier scheme="http://www.infocamere.it">{}</identifier>
                </entity>
                <period>
                  <startDate>{}</startDate>
                  <endDate>{}</endDate>
                </period>
                <scenario>
                  <itcc-ci-ese:scen>Depositato</itcc-ci-ese:scen>
                </scenario>
            </context>""".format(
            d_year,
            balance_form_data["fiscalcode"],
            balance_form_data["date_from"],
            balance_form_data["date_to"],
        )
        xbrl += """
            <unit id="eur">
                <measure>iso4217:EUR</measure>
            </unit>
            <unit id="shares">
                <measure>xbrli:shares</measure>
            </unit>
            <unit id="pure">
                <measure>xbrli:pure</measure>
            </unit>
            """
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiDenominazione", i_year, balance_form_data["company_name"]
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiSede",
            i_year,
            balance_form_data["address"]
            + " - "
            + self.env.company.zip
            + " - "
            + self.env.company.city,
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiCapitaleSociale", i_year, balance_form_data["rea_capital"], 0
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiCapitaleSocialeInteramenteVersato", i_year, "true"
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiCodiceCciaa", i_year, balance_form_data["rea_office"]
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiPartitaIva", i_year, balance_form_data["vat_code"]
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiCodiceFiscale", i_year, balance_form_data["fiscalcode"]
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiNumeroRea",
            i_year,
            balance_form_data["rea_office"] + " " + balance_form_data["rea_num"],
        )
        xbrl += self.get_xbrl_data_tag("DatiAnagraficiFormaGiuridica", i_year, "")
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiSettoreAttivitaPrevalenteAteco", i_year, ""
        )
        if self.env.company.rea_liquidation_state == "LS":
            tmp_s = "true"
        else:
            tmp_s = "false"
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiSocietaLiquidazione", i_year, tmp_s
        )
        if self.env.company.rea_member_type == "SU":
            tmp_s = "true"
        else:
            tmp_s = "false"
        xbrl += self.get_xbrl_data_tag("DatiAnagraficiSocietaSocioUnico", i_year, tmp_s)
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiSocietaSottopostaAltruiAttivitaDirezioneCoordinamento",
            i_year,
            "false",
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiDenominazioneSocietaEnteEsercitaAttivitaDirezioneCoordinamento",
            i_year,
            "",
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiAppartenenzaGruppo", i_year, "false"
        )
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiDenominazioneSocietaCapogruppo", i_year, ""
        )
        xbrl += self.get_xbrl_data_tag("DatiAnagraficiPaeseCapogruppo", i_year, "")
        xbrl += self.get_xbrl_data_tag(
            "DatiAnagraficiNumeroIscrizioneAlboCooperative", i_year, ""
        )

        if balance_form_data["values_precision"] == "d":
            decimal_precision = 2
        else:
            decimal_precision = 0
        tmp_balance_lines = self.env["account.balance.eu"].search([("code", "=", "PA")])
        if len(tmp_balance_lines) == 1:
            xbrl += self.get_balance_line_tags(
                tmp_balance_lines[0],
                balance_ue_data["balance_ue_lines"],
                i_year,
                decimal_precision,
            )
        tmp_balance_lines = self.env["account.balance.eu"].search([("code", "=", "PP")])
        if len(tmp_balance_lines) == 1:
            xbrl += self.get_balance_line_tags(
                tmp_balance_lines[0],
                balance_ue_data["balance_ue_lines"],
                i_year,
                decimal_precision,
            )
        tmp_balance_lines = self.env["account.balance.eu"].search([("code", "=", "E")])
        if len(tmp_balance_lines) == 1:
            xbrl += self.get_balance_line_tags(
                tmp_balance_lines[0],
                balance_ue_data["balance_ue_lines"],
                d_year,
                decimal_precision,
            )

        xbrl += "\n</xbrl>"
        return xbrl, "xbrl"


class BalanceEuHTMLReport(models.AbstractModel):
    _name = "report.l10n_it_account_balance_eu.balance_eu_html_report"
    _description = "Export EU Balance in HTML format"

    def _get_report_values(self, docids, data):
        balance_ue_data = self.env["account.balance.eu"].cal_balance_ue_data(data)
        return balance_ue_data
