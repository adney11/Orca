#g++ -pthread src/orca-server-mahimahi.cc src/flow.cc -o orca-server-mahimahi
#g++ src/client.c -o client
#cp client rl-module/
#mv orca-server*  rl-module/
#sudo chmod +x rl-module/client
#sudo chmod +x rl-module/orca-server-mahimahi


g++ -pthread src/orca-server-mahimahi-http.cc src/flow.cc -o orca-server-mahimahi-http
#g++ src/client.c -o client
#cp client rl-module/
mv orca-server-mahimahi-http  orca_pensieve/
sudo chmod +x orca_pensieve/orca-server-mahimahi-http


