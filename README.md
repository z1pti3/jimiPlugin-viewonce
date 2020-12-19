# jimiPlugin-viewonce
Secure token link encrypted sharing method for view once type data e.g. tokens and passwords

Requires a data folder and within it a public and private key ( build them just like you did for jimi session keys, but make sure they are not the same )

Viewonce data is encpyted using AES 256 with a random key encpyted by the RSA public key. the random key is then returned as a token along with the ID of the viewonce data and 50% of the encpyted data.

The database alone does not contain the full viewonce enctpyted message but only 50% of it is stored within the database.

This plugin is ideal for when jimi creates or resets passwords on accounts and you want a way to send the password to a user without storing it for a long preiod of time - remember auth is not required to read the data save within the plugin so ensure the link is transmiitted in a secure way i.e. over HTTPS
