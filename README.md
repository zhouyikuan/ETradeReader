# ETradeReader
A minimal implementation that accesses eTrade APIs using python

This is a minimal implementation that accesses eTrade APIs using python.

Prerequisites:
  1. Own an eTrade brokerage account
  2. Be registered with the eTrade API (Although not mandatory, it is recommended to have set up a callback url)

How it works:
  1. Populate the following from the eTrade API: app_key and app_secret
  2. Call generate_request_code() and generate the request_token & request_token_secret
  3. Generate the URL by invoking generate_authorization_url()
     
           Note: If a callback url is configured with eTrade API, the verifier code will be delivered through
             the callback so that generate_access_token() can be automatically executed.
             Otherwise, the verifier code will be displayed on the webpage and generate_access_token() needs
             to be executed manually.
  5. After generate_access_token() is executed, the access_token & access_token_secret should be saved.
  6. With access_token & access_token_secret ready, various APIs can be invoked such as get_stock_price()     

Note:

    Ensure request_token, request_token_secret are preserved between steps (2) generate_request_code() 
    and (4) generate_access_token() by storing them externally (ex. a file/database)
    
    After obtaining access_token & access_token_secret, these can also be saved for later usage.
