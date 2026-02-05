import axios from 'axios';
import type { CartItem } from '../context/CartContext';

const API_BASE = '/api';

export interface CartInvoiceBreakdownItem {
    name: string;
    unit_price: number;
    unit_price_eur: number;
    quantity: number;
    subtotal_eur: number;
}

export interface CartInvoiceShop {
    shop: string;
    status: 'CALCULATED' | 'PENDING_RULES';
    items: CartInvoiceBreakdownItem[];
    total_items_qty?: number;
    shipping_eur: number;
    tax_eur: number;
    fees_eur?: number;
    total_eur: number;
}

export interface CartInvoice {
    breakdown: CartInvoiceShop[];
    grand_total_eur: number;
    user_location: string;
    timestamp: string;
}

export const calculateCart = async (items: CartItem[]): Promise<CartInvoice> => {
    const userId = localStorage.getItem('active_user_id') || '2';
    const response = await axios.post(`${API_BASE}/logistics/calculate-cart`, {
        items: items.map(i => ({
            product_name: i.product_name,
            shop_name: i.shop_name,
            price: i.price,
            quantity: i.quantity
        })),
        user_id: parseInt(userId)
    });
    return response.data;
};
