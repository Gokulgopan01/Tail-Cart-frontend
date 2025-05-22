import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from the environment variables
API_KEY = os.getenv('API_KEY')

class HybridBPOApi:

    def __init__(self):
        
        self.API_KEY=API_KEY

    

    def loadPortals():

        # api call to load all the portal
        1

    def loadAccounts():
        #api clal to load all the accounts of a user
        1

    def check_application_version():

        return True

    #etc..etc..

    def get_order (self, orderId):
        
        try:
            print("order fetching")
            # api call to get the order details using the order_id
            # order={"orderId":"1010","mls_id":{"a1_mls_id":"20555125824","a2_mls_id":"10380960","a3_mls_id":"8498435","a4_mls_id":"8498436","a5_mls_id":"8498437","a6_mls_id":"8498438"},"Address":"2808 MIRA VISTA LN Rockwall TX 75032","MLS":"GAMLS","Username" :"dawsonlabres","Password":"love", "Path":"S:\\Anisha\\Comparable PIC-PDF Download\\2808 MIRA VISTA LN Rockwall TX 75032"}
            order={"orderId":"1010","mls_id":{"a1_mls_id":"7498101","a2_mls_id":"7498178","a3_mls_id":"7498179","a4_mls_id":"7498180","a5_mls_id":"7498181","a6_mls_id":"7498182"},"Address":"911 Providence Way, Lawrenceville, GA 30046","MLS":"FMLS","Username" :"msreed","Password":"Ledarion#08", "Path":"S:\\Anisha\\Comparable PIC-PDF Download\\911 Providence Way, Lawrenceville, GA 30046"}
            print("Order found")
            return order      
        except Exception as e:
            print(f"Error in the program: {e}")

    def get_entry_order():
        """Returns the order details as a dictionary."""
        order_details = [
     
        # {
        #     "order_id": 58,
        #     "client_name": "Ecesis",
        #     "main_client": "Roselyn",
        #     "portal_name": "RedBell",
        #     "portal_id": 2,
        #     "portal_url": "https://valuationops.homegenius.com/VendorPortal",
        #     "username": "silvercirclebpos@gmail.com",
        #     "password": "Re@2025bpo",
        #     "session": "6A3CBEDB74088199B26921AF230D081C45D58C0897DC6399CE109593757393A83C73DA4C3E9604D609C97A7F002AEE2A610FE469B9B6D932CB6522BB8EDD56DEF597713E2EF71B4927D828AD837CE62B97E8DE4FB48CFED263A54B2814C742B9444DF8273EC3C587DA231DA82250A83D24AD471BA98BE8EAE214B0D05CAA58CC523E8C92E12E82CBEE5230993B69083A1C802D43C78702073D7AB5DD41172EC844930A7FC36AFE027B6308E1628F811C56A72D595F08414F0A50E9C6ACFC27C4F5454405934B717E99228FD34CC69B7C6161697741B2A8DC094F8BF3846D75543AF4F9FBC04CE77FECC5F6881B98194797A8C3EA01E8C60457FF914156300C57C60DE70D8955ECA4E18DC2DBF013AAA2406439D5843BC4710F890531A485FD2984CA83778D7C6F65DD259CAA2A342F56427E4D3E469C8119253521578C93910A10A38EC317937B5B8740B214F318641B4C200C7ACAA8D8CEE14A3E2822F89FC9B2159132",
        #     "__RequestVerificationToken": "SDaZfMfKH9Q8hyTeQqiBBG5A7QMWUY7hoGRDqE4-BPdvj-av_RU7zouQLnzn9hPffTIym27e-E1UflrTGVEoTzl0KX81",
        #     "proxy": "",
        #     "account_status": "Active"
        # }

             
        {
            "order_id": 58,
            "client_name": "Bang",
            "main_client": "Betty Spradley",
            "portal_name": "RedBell",
            "portal_id": 2,
            "portal_url": "https://valuationops.homegenius.com/VendorPortal",
            "username": "memphisbpo@bangrealty.com",
            "password": "Louisespra127$0$",
            "session": "D66BA2D5A397DFD02FE53403DE4D9C1FAC2D8E3D35D47F8BBDFB010F32CEAD2B2370D0D1108F698847701A5AECB1D155B98E1ADD3DFCF1F5A05881A98F15E6AD56802E6BA518009D805498E84C5F6D2F473EA34F0A6BCD39CFF2253DD32ED66724DFBF30325F8C7660AFF10500029AE4EBE571841745741AE5B5032B745647B34772F63B8E3CF5D559FABD78D00587C1303008F3200E342073DB2F2C268025159D439FA217E055A71B648E4B25704FBF6B4BFD584DDB92E3B0DDB180D892E6AACF825BAF311A6FAA67E5533DA4FFC527A4E405EC99D425A7E23A6B96EE09FA845C540846CB962A48D7C1E49F3B28F06380138E2B9BB069782B49FD4870766BB7C747D7054E74BC5C1CC2C69F3506C1FB247FDA41C428B80567958EF6DCF162094EA06F5A52F10A945E248B64E256AB09F650FF02589D36F01A70753D482CD8DD9B2EAEC9DCF04D05F44F288CF50873C76FB94E82",
            "__RequestVerificationToken": "SDaZfMfKH9Q8hyTeQqiBBG5A7QMWUY7hoGRDqE4-BPdvj-av_RU7zouQLnzn9hPffTIym27e-E1UflrTGVEoTzl0KX81",
            "proxy": "",
            "account_status": "Active"
        }
        # {
        #     "order_id": 10,
        #     "client_name": "Keystone Holdings",
        #     "main_client": "KSH_AudreyWilliams",
        #     "portal_name": "Proteck",
        #     "portal_id": 12,
        #     "portal_url": "https://www.protk.com/net/Entry.aspx",
        #     "username": "Audrey63",
        #     "password": "0cg3hyKq",
        #     "session": "",
        #     "proxy": "",
        #     "account_status": "Active"
        # }
        ]
        return order_details

    