import requests
import base64
from datetime import datetime
import json
from flask import current_app
import os

class MpesaAPI:
    def __init__(self):
        self.consumer_key = os.environ.get('MPESA_CONSUMER_KEY', 'ZzEqDAMIrOhLPcKG2oWwFQ9A5dwanJUzfhfPPh34kLoJwrqq')
        self.consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET', '5yJNzoKGxqOrv3UZhIUHZG03vKk1s1bPJwm4MDw93alnIvoiMRr5o6q1UL146L06')
        self.api_url = 'https://sandbox.safaricom.co.ke'  # Change to production URL in production
        self.access_token = None

    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
            headers = {
                'Authorization': f'Basic {auth}'
            }
            
            response = requests.get(
                f"{self.api_url}/oauth/v1/generate?grant_type=client_credentials",
                headers=headers
            )
            
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                return self.access_token
            return None
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return None

    def format_phone_number(self, phone_number):
        """Format phone number to required format (254XXXXXXXXX)"""
        # Remove any spaces or special characters
        phone = ''.join(filter(str.isdigit, phone_number))
        
        # Handle different formats
        if phone.startswith('0'):  # 0712345678
            phone = '254' + phone[1:]
        elif phone.startswith('+'):  # +254712345678
            phone = phone[1:]
        elif not phone.startswith('254'):  # 712345678
            phone = '254' + phone
            
        return phone

    def validate_phone_number(self, phone_number):
        """Validate phone number format"""
        phone = self.format_phone_number(phone_number)
        if not phone.startswith('254') or len(phone) != 12:
            return False, "Invalid phone number format. Please use format: 07XXXXXXXX"
        return True, phone

    def initiate_stk_push(self, phone_number, amount, reference, callback_url):
        """Initiate STK Push transaction"""
        # Validate phone number
        is_valid, phone_or_error = self.validate_phone_number(phone_number)
        if not is_valid:
            return None, phone_or_error

        # Get access token if not available
        if not self.access_token:
            self.get_access_token()

        if not self.access_token:
            return None, "Could not connect to M-Pesa. Please try again."

        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"174379{os.environ.get('MPESA_PASSKEY')}{timestamp}".encode()
            ).decode()

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                "BusinessShortCode": "174379",  # Your business shortcode
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_or_error,  # Validated phone number
                "PartyB": "174379",  # Your business shortcode
                "PhoneNumber": phone_or_error,
                "CallBackURL": callback_url,
                "AccountReference": reference,
                "TransactionDesc": "Payment for Qaffee Point order"
            }

            response = requests.post(
                f"{self.api_url}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                # Add user-friendly message
                result['user_message'] = "Please enter your M-Pesa PIN to complete payment"
                return result, None
                
            # Handle specific error cases
            error_msg = response.text
            if "Invalid Access Token" in error_msg:
                return None, "Connection to M-Pesa failed. Please try again."
            elif "Invalid PhoneNumber" in error_msg:
                return None, "Invalid phone number. Please check and try again."
            elif "Invalid Amount" in error_msg:
                return None, "Invalid amount. Please try again."
            else:
                return None, "Could not initiate M-Pesa payment. Please try again."

        except requests.exceptions.ConnectionError:
            return None, "Could not connect to M-Pesa. Please check your internet connection."
        except Exception as e:
            return None, f"Error initiating payment: {str(e)}"

    def verify_transaction(self, checkout_request_id):
        """Verify transaction status"""
        if not self.access_token:
            self.get_access_token()

        if not self.access_token:
            return None, "Could not connect to M-Pesa. Please try again."

        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"174379{os.environ.get('MPESA_PASSKEY')}{timestamp}".encode()
            ).decode()

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                "BusinessShortCode": "174379",
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }

            response = requests.post(
                f"{self.api_url}/mpesa/stkpushquery/v1/query",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                # Add user-friendly status messages
                if result.get('ResultCode') == '0':
                    result['user_message'] = "Payment completed successfully"
                elif result.get('ResultCode') == '1037':
                    result['user_message'] = "Payment timeout. Please try again."
                elif result.get('ResultCode') == '1032':
                    result['user_message'] = "Payment cancelled. Please try again."
                elif result.get('ResultCode') == '1001':
                    result['user_message'] = "Waiting for your M-Pesa PIN..."
                else:
                    result['user_message'] = "Payment failed. Please try again."
                return result, None
                
            return None, "Could not verify payment status. Please try again."

        except requests.exceptions.ConnectionError:
            return None, "Could not connect to M-Pesa. Please check your internet connection."
        except Exception as e:
            return None, "Error verifying payment status. Please try again." 