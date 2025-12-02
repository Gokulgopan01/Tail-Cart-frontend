from utility.redbell import best_sold_or_active_address, date_conversion, yesterday_date_conversion


def generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3):
    """
    Generate condition data dictionary based on extracted sections.
    """

    condition_data = {}

    # 1. Conditions from sub_data
    if sub_data:
        inspection_date = sub_data.get("InspectionDate")
        current_list_date=sub_data.get("CurrentListingDate")
        original_list_date=sub_data.get("OriginalListDateListing")
        last_list_date=sub_data.get("LastListDate")
        original_sold_date=sub_data.get("OriginalListDateSold")
        Hoa_fees_include_checkbox_values = sub_data.get("HOAFeesInclude", [])  
        BestSold=sub_data.get("BestSold")
        BestActive=sub_data.get("BestActive")
        # property_type = sub_data.get("PropertyType")
        # pool = sub_data.get("Pool")
        # year_built = sub_data.get("YearBuilt")

        if inspection_date:
            condition_data["InspectionDate"] = yesterday_date_conversion()
        if current_list_date:
            condition_data["CurrentListingDate"]=date_conversion(current_list_date)  
        if original_list_date:
            condition_data["OriginalListDateListing"]=date_conversion(original_list_date)
        if  last_list_date:
             condition_data["LastListDate"]=date_conversion(last_list_date) 
        if original_sold_date:
             condition_data["OriginalListDateSold"]=date_conversion(original_sold_date) 
        

        condition_data['BestActive']=best_sold_or_active_address(BestActive)
        condition_data['BestSold']=best_sold_or_active_address(BestSold)
         
        if condition_data['BestActive']:
            if condition_data['BestActive'] in list1.get('Address', ''):
                condition_data['BestActivecomp'] = '1'
            elif condition_data['BestActive']in list2.get('Address', ''):
                condition_data['BestActivecomp'] = '2'
            elif condition_data['BestActive']in list3.get('Address', ''):
                condition_data['BestActivecomp'] = '3'
            else:
                condition_data['BestActivecomp'] = ''
        else:
            condition_data['BestActivecomp'] = ''

   
        if condition_data['BestSold']:
            if condition_data['BestSold'] in sold1.get('Address', ''):
                condition_data['BestSoldcomp'] = '1'
            elif condition_data['BestSold'] in sold2.get('Address', ''):
                condition_data['BestSoldcomp'] = '2'
            elif condition_data['BestSold'] in sold3.get('Address', ''):
                condition_data['BestSoldcomp'] = '3'
            else:
                condition_data['BestSoldcomp'] = ''
        else:
            condition_data['BestSoldcomp'] = ''                
    if list1:
        current_list1date=list1.get("CurrentListingDate")
        orginal_list1_date=list1.get("OriginalListDateListing") 
        if current_list1date:
            condition_data["current_list1date"]=date_conversion(current_list1date)
        if orginal_list1_date:
            condition_data["orginal_list1_date"]=date_conversion(orginal_list1_date)    
    if list2:
        current_list2date=list2.get("CurrentListingDate")
        orginal_list2_date=list2.get("OriginalListDateListing") 
        if current_list2date:
            condition_data["current_list2date"]=date_conversion(current_list2date)
        if orginal_list2_date:
            condition_data["orginal_list2_date"]=date_conversion(orginal_list2_date)     
    if list3:        
        current_list3date=list3.get("CurrentListingDate")  
        orginal_list3_date=list3.get("OriginalListDateListing")    
        if current_list3date:
            condition_data["current_list3date"]=date_conversion(current_list3date)        
        if orginal_list3_date:
            condition_data["orginal_list3_date"]=date_conversion(orginal_list3_date) 
    if  sold1:
        current_sold1date= sold1.get("CurrentListingDate")
        orginal_sold1_date= sold1.get("OriginalListDateListing") 
        sale_sold1_date=sold1.get("SaleDate")
        if current_sold1date:
            condition_data["current_sold1date"]=date_conversion(current_sold1date)
        if orginal_sold1_date:
            condition_data["orginal_sold1_date"]=date_conversion(orginal_sold1_date) 
        if sale_sold1_date:
            condition_data['sale_sold1_date']=date_conversion(sale_sold1_date)       
    if  sold2:
        current_sold2date= sold2.get("CurrentListingDate")
        orginal_sold2_date= sold2.get("OriginalListDateListing") 
        sale_sold2_date=sold2.get("SaleDate")
        if current_sold2date:
            condition_data["current_sold2date"]=date_conversion(current_sold2date)
        if orginal_sold2_date:
            condition_data["orginal_sold2_date"]=date_conversion(orginal_sold2_date) 
        if sale_sold2_date:
            condition_data['sale_sold2_date']=date_conversion(sale_sold2_date)        
    if  sold3:        
        current_sold3date= sold3.get("CurrentListingDate")  
        orginal_sold3_date= sold3.get("OriginalListDateListing")   
        sale_sold3_date=sold3.get("SaleDate") 
        if current_sold3date:
            condition_data["current_sold3date"]=date_conversion(current_sold3date)        
        if orginal_sold3_date:
            condition_data["orginal_sold3_date"]=date_conversion(orginal_sold3_date) 
        if sale_sold3_date:
            condition_data['sale_sold3_date']=date_conversion(sale_sold3_date)      

      

    return condition_data
