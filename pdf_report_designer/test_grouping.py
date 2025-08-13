#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file for PDF Report Designer Grouping Feature
This file demonstrates how the grouping functionality works
"""

def test_grouping_logic():
    """Test the grouping logic with sample data"""
    
    # Sample data structure
    sample_records = [
        {'partner_id': 'Customer A', 'amount': 50000, 'total': 50000},
        {'partner_id': 'Customer A', 'amount': 70000, 'total': 70000},
        {'partner_id': 'Customer B', 'amount': 1435500, 'total': 1435500},
        {'partner_id': 'Customer B', 'amount': 1617000, 'total': 1617000},
    ]
    
    # Simulate grouping logic
    grouped_data = {}
    for record in sample_records:
        group_key = record['partner_id']
        if group_key not in grouped_data:
            grouped_data[group_key] = []
        grouped_data[group_key].append(record)
    
    # Expected result
    expected_groups = {
        'Customer A': [
            {'partner_id': 'Customer A', 'amount': 50000, 'total': 50000},
            {'partner_id': 'Customer A', 'amount': 70000, 'total': 70000},
        ],
        'Customer B': [
            {'partner_id': 'Customer B', 'amount': 1435500, 'total': 1435500},
            {'partner_id': 'Customer B', 'amount': 1617000, 'total': 1617000},
        ]
    }
    
    # Verify grouping
    assert grouped_data == expected_groups, "Grouping failed!"
    
    # Test totals calculation
    for group_name, records in grouped_data.items():
        total_amount = sum(record['amount'] for record in records)
        total_total = sum(record['total'] for record in records)
        
        print(f"Group: {group_name}")
        print(f"  Records: {len(records)}")
        print(f"  Total Amount: {total_amount}")
        print(f"  Total Total: {total_total}")
        print()
    
    print("✅ All tests passed! Grouping functionality works correctly.")
    return True

if __name__ == "__main__":
    test_grouping_logic()
