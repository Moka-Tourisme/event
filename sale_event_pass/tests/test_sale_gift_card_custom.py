from odoo.addons.sale_gift_card.tests.common import TestSaleGiftCardCommon

class GiftCardDesignTest(TestSaleGiftCardCommon):

    def test_buying_simple_gift_card(self):
        order = self.empty_order
        order.write({'order_line': [
            (0, False, {
                'product_id': self.product_A.id,
                'name': 'Ordinary Product A',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
            }),
            (0, False, {
                'product_id': self.product_gift_card.id,
                'name': 'Gift Card Product',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
            })
        ]})
        self.assertEqual(len(order.order_line.ids), 2)
        self.assertEqual(order.gift_card_count, 0)
        self.assertEqual(len(order.order_line.mapped('generated_gift_card_ids')), 0)
        order.action_confirm()
        # After Confirmation
        self.assertEqual(order.gift_card_count, 1)
        self.assertEqual(len(order.order_line.mapped('generated_gift_card_ids')), 1)

        self.assertEqual(order.order_line.filtered(lambda sale_order_line:sale_order_line.product_id == self.product_gift_card).generated_gift_card_ids.product_template_id, self.product_gift_card.product_tmpl_id)
