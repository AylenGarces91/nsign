from odoo import models, fields, api
from odoo.tools import ormcache


class L10nResPartnerCustom(models.Model):
    _inherit = 'res.partner'
    
    @ormcache("self.vat, self.country_id")
    def _parse_aeat_vat_info000(self):
        """Return tuple with split info (country_code, identifier_type and
        vat_number) from vat and country partner
        """
        try:
            self.ensure_one()
            vat_number = self.vat or ""
            prefix = self._map_aeat_country_code(vat_number[:2].upper())
            if prefix in self._get_aeat_europe_codes():
                country_code = prefix
                vat_number = vat_number[2:]
                identifier_type = "02"
            else:
                country_code = self._map_aeat_country_code(self.country_id.code) or ""
                if country_code in self._get_aeat_europe_codes():
                    identifier_type = "02"
                else:
                    identifier_type = "04"
            if country_code == "ES":
                identifier_type = ""
            return country_code, identifier_type, vat_number
        except:
            return "", "", ""
