pyinstaller --name "autologinuat" --splash "assets/splash_logo.jpg" --onefile --noconsole --add-data "assets\;assets" --add-data "screens/json/portal_map.json;json" --add-data ".env;." --add-data "json\;json" --add-data "assets\logo.jpg;assets" autologinuat.py --hidden-import=pyi_splash 



pyinstaller --name "autologin" --splash "assets/splash_logo.jpg" --onefile --noconsole --add-data "assets\;assets" --add-data "screens/json/portal_map.json;json" --add-data ".env;." --add-data "json\;json" --add-data "assets\logo.jpg;assets" autologin.py --hidden-import=pyi_splash 
