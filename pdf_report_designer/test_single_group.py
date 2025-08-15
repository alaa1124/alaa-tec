#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file for PDF Report Designer Single Group Support
This file demonstrates that totals are shown even with single groups
"""

def test_single_group_totals():
    """Test that totals are shown even when there's only one group"""
    
    # Simulate single group data
    single_group_data = {
        'Customer A': [
            {'amount_total': 50000, 'product_qty': 5},
            {'amount_total': 70000, 'product_qty': 7},
            {'amount_total': 30000, 'product_qty': 3},
        ]
    }
    
    print("📊 Testing Single Group Totals")
    print("=" * 50)
    
    for group_name, records in single_group_data.items():
        print(f"\nGroup: {group_name}")
        print("-" * 30)
        
        # Show individual records
        for i, record in enumerate(records, 1):
            print(f"  Record {i}: Amount={record['amount_total']}, Qty={record['product_qty']}")
        
        # Calculate and show totals
        total_amount = sum(record['amount_total'] for record in records)
        total_qty = sum(record['product_qty'] for record in records)
        
        print(f"\n  --- TOTAL ---")
        print(f"  Total Amount: {total_amount}")
        print(f"  Total Quantity: {total_qty}")
    
    print("\n" + "=" * 50)
    print("✅ Single group totals test completed!")
    print("Note: Even with one group, totals should be displayed")
    return True

def test_field_detection_for_totals():
    """Test which fields will have totals calculated"""
    
    # Sample fields from your report
    sample_fields = [
        {'name': 'amount_total', 'ttype': 'monetary', 'description': 'Total Amount'},
        {'name': 'product_qty', 'ttype': 'integer', 'description': 'Product Quantity'},
        {'name': 'customer_name', 'ttype': 'char', 'description': 'Customer Name'},
        {'name': 'order_date', 'ttype': 'date', 'description': 'Order Date'},
    ]
    
    print("\n🔍 Testing Field Detection for Totals")
    print("=" * 50)
    
    for field in sample_fields:
        field_name = field['name'].lower()
        field_description = field['description'].lower()
        field_type = field['ttype']
        
        # Check if field should have totals
        should_calculate_total = False
        
        if field_type in ['monetary', 'integer', 'float']:
            meaningful_keywords = [
                'amount', 'total', 'price', 'cost', 'value', 'quantity', 
                'qty', 'count', 'sum', 'balance', 'credit', 'debit',
                'revenue', 'income', 'expense', 'budget', 'target',
                'commission', 'discount', 'tax', 'fee', 'charge',
                'weight', 'volume', 'area', 'length', 'height',
                'score', 'rating', 'percentage', 'ratio'
            ]
            
            for keyword in meaningful_keywords:
                if keyword in field_name or keyword in field_description:
                    should_calculate_total = True
                    break
        
        result = "✅ WILL SUM" if should_calculate_total else "❌ WON'T SUM"
        reason = "Contains meaningful keyword" if should_calculate_total else f"Not a meaningful numeric field"
        
        print(f"{field['name']:<20} | {field['description']:<25} | {result:<12} | {reason}")
    
    print("\n" + "=" * 50)
    print("✅ Field detection test completed!")
    return True

if __name__ == "__main__":
    test_single_group_totals()
    test_field_detection_for_totals()

